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
use Carbon\Carbon;
use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;

class ApiClient
{
    private Client $guzzle;

    public function __construct()
    {
        $this->guzzle = new Client(['base_uri' => 'https://api.kraken.com']);
    }

    public function getServerTime(): Carbon
    {
        $result = $this->call('/0/public/Time')['result'];

        return new Carbon($result['rfc1123']);
    }

    /**
     * @throws KrakenServerException
     * @throws \GuzzleHttp\Exception\GuzzleException
     * @throws KrakenClientException
     * @throws \JsonException
     */
    private function call(string $endpoint): array
    {
        try {
            $response = $this->guzzle->get($endpoint);
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
}