<?php
declare(strict_types=1);

namespace App\Kraken\Exception;


class KrakenClientException extends KrakenApiException
{
    private string $severity;
    private string $category;
    private array $messages;
    private array $result;

    public function __construct(string $severity, string $category, array $messages, array $result)
    {
        array_unshift($messages, $category);
        parent::__construct(implode("\n", $messages), $severity === 'W' ? 0 : 1);

        $this->severity = $severity;
        $this->category = $category;
        $this->messages = $messages;
        $this->result = $result;
    }

    /**
     * @return string
     */
    public function getSeverity(): string
    {
        return $this->severity;
    }

    /**
     * @return string
     */
    public function getCategory(): string
    {
        return $this->category;
    }

    /**
     * @return array
     */
    public function getMessages(): array
    {
        return $this->messages;
    }

    /**
     * @return array
     */
    public function getResult(): array
    {
        return $this->result;
    }
}