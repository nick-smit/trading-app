<?php

namespace App\Console\Commands\Kraken;

use App\Kraken\ApiClient;
use App\Trading\Wallet;
use GuzzleHttp\Exception\ConnectException;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\Console\Output\OutputInterface;
use function MongoDB\BSON\toPHP;

class Trade extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'kraken:trade {--debug}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Trades EUR for BTC';
    /**
     * @var null
     */
    private $currentPosition;

    /**
     * Execute the console command.
     *
     * @return int
     */
    public function handle(ApiClient $apiClient)
    {
        $this->wallet = new Wallet(['USD' => 500]);
        $this->currentPosition = null;

        $movingAvgLengthInSeconds = 40;
        $timoutBetweenCalls = 2;
        $minimumTrendLengthToBaseDecisionsOn = $movingAvgLengthInSeconds / $timoutBetweenCalls;
        $tradeSize = 0.02;
        $stopLossPercent = 0.0025;
        $stopWinPercent = 0.05;

        $this->info("Starting startup sequence");
        $movingAvg = [];
        for ($i = 0; $i < $movingAvgLengthInSeconds; $i+=$timoutBetweenCalls) {
            $price = $this->getBtcusdPrice($apiClient);
            $movingAvg[] = $price;
            $this->info(sprintf("Current BTCUSD price %f", $price));

            sleep($timoutBetweenCalls);
        }

        while (true) {
            // Run loop
            try {
                $price = $this->getBtcusdPrice($apiClient);
            } catch (ConnectException $e) {
                $this->warn('Connection timed out');
                continue;
            }

            // Calculate the moving average
            array_shift($movingAvg);
            $movingAvg[] = $price;

            $lastTrend = $trend ?? 0;
            $trendArr = [];
            for ($i = 1; $i < $minimumTrendLengthToBaseDecisionsOn; $i++) {
                $trendArr[] = $movingAvg[$i] - $movingAvg[$i-1];
            }
            $trend = array_sum($trendArr) / $minimumTrendLengthToBaseDecisionsOn;

            if ($this->option('debug')) {
                $movingAvgPrice = array_sum($movingAvg) / ($movingAvgLengthInSeconds / $timoutBetweenCalls);
                $this->info(sprintf("Current BTCUSD price %f moving average is %f and the trend is %f", $price, $movingAvgPrice, $trend));
            }

            if ($this->currentPosition === null) {
                if ($trend > 2.5 && array_sum($trendArr) > 0) {
                    $availableMoney = $this->wallet->getUsd() * $tradeSize;
                    $quantity = $availableMoney / $price;

                    // Buy!
                    $stoploss = $price * (1 - $stopLossPercent);
                    $this->currentPosition = [
                        'buy_price' => $price,
                        'fee' => $this->calculateInitialFee($price, $availableMoney, $quantity),
                        'buy_time' => time(),
                        'stop_loss' => $stoploss,
                        'stop_win' => $price * (1 + $stopWinPercent),
                        'BTC_amount' => $quantity,
                        'top_price' => $price,
                    ];
                    $this->wallet->withdraw('USD', $availableMoney);
                    $this->wallet->deposit('BTC', $this->currentPosition['BTC_amount']);

                    $this->info(sprintf("Bought %f BTC at a price of %f (stoploss: %f)", $quantity, $price, $stoploss));
                }
            } else {
                if ($price > $this->currentPosition['top_price']) {
                    $this->currentPosition['top_price'] = $price;
                }

                $sell = false;
                $reason = '';
                if ($price < $this->currentPosition['stop_loss']) {
                    $sell = true;
                    $reason = 'stoploss';
                } else if ($price > $this->currentPosition['stop_win']  && $trend < 0) {
                    $sell = true;
                    $reason = 'Stop win';
//                } else if ($price > $this->currentPosition['buy_price'] &&
//                    $price < ($this->currentPosition['top_price'] * 0.9975 - (($this->currentPosition['fee'] * 2) / $this->currentPosition['BTC_amount']))) {
//                    $sell = true;
//                    $reason = 'Dipped 0.25% after top price';
                }

                if ($sell) {
                    $this->calculateClosingfee($price);

                    $buyPrice = $this->currentPosition['buy_price'] * $this->currentPosition['BTC_amount'];
                    $sellPrice = $price * $this->currentPosition['BTC_amount'];
                    $profit = $sellPrice - $buyPrice - $this->currentPosition['fee'];
                    $this->wallet->withdraw('BTC', $this->currentPosition['BTC_amount']);
                    $this->wallet->deposit('USD', $sellPrice - $this->currentPosition['fee']);

                    $this->info(sprintf("Sold %f BTC at a price of %f and made %f profit (fee: %f), reason: %s, wallet worth in USD: %f", $quantity, $price, $profit, $this->currentPosition['fee'], $reason, $this->wallet->getUsd()));

                    $this->currentPosition = null;
                }
            }

            sleep($timoutBetweenCalls);
        }

        return 0;
    }

    public function line($string, $style = null, $verbosity = null)
    {
        parent::line(sprintf('[%s] - %s', date('d-m-Y H:i:s'), $string), $style, $verbosity);
    }

    /**
     * @param ApiClient $apiClient
     * @return mixed
     */
    private function getBtcusdPrice(ApiClient $apiClient): float
    {
        return (float) $apiClient->getTickerInformation('BTCUSD')['result']['XXBTZUSD']['c'][0];
    }

    private function calculateInitialFee(float $price, float $availableMoney, float $quantity)
    {
        $f = ($quantity * $availableMoney) / 100;
        return $f * 0.26 + $f * 0.02;
    }

    private function calculateClosingfee(float $currentPrice)
    {
        $fee = $this->currentPosition['fee'];

        $fourHours = 14400;
        $positionOpenDuration = time() - $this->currentPosition['buy_time'];
        $f = $currentPrice * $this->currentPosition['BTC_amount'];
        if ($positionOpenDuration > $fourHours) {
            $fee += $f * ($positionOpenDuration % $fourHours) * 0.02;
        }

        $fee += ($f / 100) * 0.26;
        $this->currentPosition['fee'] = $fee;
    }
}
