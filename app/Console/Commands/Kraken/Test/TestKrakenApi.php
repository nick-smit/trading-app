<?php

namespace App\Console\Commands\Kraken\Test;

use App\Kraken\ApiClient;
use App\Kraken\Exception\KrakenApiException;
use Illuminate\Console\Command;

class TestKrakenApi extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'kraken:test-api';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Checks if we can call the kraken api';

    /**
     * Execute the console command.
     *
     * @return int
     */
    public function handle(ApiClient $krakenApiClient)
    {
        $this->info("Testing getServerTime (public)");

        try {
            $serverTime = $krakenApiClient->getServerTime();
        } catch (KrakenApiException $exception) {
            $this->warn('Failed to get kraken server time');
            $this->debug($exception->getMessage());
            return 1;
        }

        $this->info('Kraken server time is ' . $serverTime->toString());

        return 0;
    }
}
