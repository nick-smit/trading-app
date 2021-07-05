<?php
declare(strict_types=1);

namespace App\Kraken;


use App\Kraken\Exception\KrakenClientAPIException;
use App\Kraken\Exception\KrakenClientAuthException;
use App\Kraken\Exception\KrakenClientException;
use App\Kraken\Exception\KrakenClientFundingException;
use App\Kraken\Exception\KrakenClientGeneralException;
use App\Kraken\Exception\KrakenClientOrderException;
use App\Kraken\Exception\KrakenClientQueryException;
use App\Kraken\Exception\KrakenClientServiceException;
use App\Kraken\Exception\KrakenClientTradeException;
use App\Kraken\Exception\KrakenClientUnknownException;
use App\Kraken\Exception\KrakenServerException;
use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;
use GuzzleHttp\RequestOptions;

class ApiClient
{
    private Client $guzzle;
    private string $apiKey;
    private string $privateKey;

    public function __construct(string $apiKey, string $privateKey)
    {
        $this->guzzle = new Client(['base_uri' => 'https://api.kraken.com']);
        $this->apiKey = $apiKey;
        $this->privateKey = $privateKey;
    }

    public function getAccountBalance(): array
    {
        return $this->call('/0/private/Balance');
    }

    public function getAssets(): array
    {
        return $this->call('/0/public/Assets');
    }

    public function getTickerInformation(string $tickerPair)
    {
        return $this->call('/0/public/Ticker', ['pair' => $tickerPair]);
    }

    /**
     * @throws KrakenServerException
     * @throws \GuzzleHttp\Exception\GuzzleException
     * @throws KrakenClientException
     * @throws \JsonException
     */
    private function call(string $endpoint, array $payload = []): array
    {
        $headers = [
            'Content-Type' => 'application/x-www-form-urlencoded'
        ];

        $nonce = $this->getNonce();
        $payload = array_merge($payload, ['nonce' => $nonce]);

        $method = 'GET';
        $payloadKey = RequestOptions::QUERY;
        if (str_contains($endpoint, 'private')) {
            $headers['API-Key'] = $this->apiKey;
            $headers['API-Sign'] = $this->getSignature($endpoint, $payload, $nonce);
            $method = 'POST';
            $payloadKey = RequestOptions::FORM_PARAMS;
        }

        try {
            $response = $this->guzzle->request($method, $endpoint, [
                RequestOptions::TIMEOUT => 5,
                $payloadKey => $payload,
                RequestOptions::HEADERS => $headers,
            ]);
        } catch (RequestException $exception) {
            throw new KrakenServerException('Kraken api responded with non 200 response code', $exception->getCode(), $exception);
        }

        $responseContent = json_decode($response->getBody()->getContents(), true, 512, JSON_THROW_ON_ERROR);

        if (!empty($responseContent['error'])) {
            throw $this->errorResponseToException($responseContent);
        }

        return $responseContent;
    }

    private function errorResponseToException(array $response): KrakenClientException
    {
        $error = explode(":", $response['error']);

        $severity = substr($error[0], 0, 1);
        $category = substr($error[0], 1);

        array_shift($error); // shift the first element off the array
        $messages = $error;

        $exceptionClass = match ($category) {
            'API' => KrakenClientAPIException::class,
            'Auth' => KrakenClientAuthException::class,
            'Funding' => KrakenClientFundingException::class,
            'General' => KrakenClientGeneralException::class,
            'Order' => KrakenClientOrderException::class,
            'Query' => KrakenClientQueryException::class,
            'Service' => KrakenClientServiceException::class,
            'Trade' => KrakenClientTradeException::class,
            default => KrakenClientUnknownException::class,
        };

        return new $exceptionClass($severity, $category, $messages, $response['result']);
    }

    public function getNonce(): string
    {
        [$msec, $sec] = explode(' ', microtime());
        // raspbian 32-bit integer workaround
        // https://github.com/ccxt/ccxt/issues/5978
        // return (int) ($sec . substr($msec, 2, 3));
        return $sec . substr($msec, 2, 3);
    }

    private function getSignature(string $apiPath, array $payload, string $nonce)
    {
        $encodedPostdata = http_build_query($payload);
        $hash = \hash('sha256', $nonce . $encodedPostdata, true);
        $secret = base64_decode($this->privateKey);
        $hmac = hash_hmac('sha512', $apiPath . $hash, $secret, true);

        return base64_encode($hmac);
    }
}