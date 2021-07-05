<?php
declare(strict_types=1);

namespace App\Trading;


class Wallet
{
    /**
     * @var array
     */
    private $positions;

    public function __construct(array $positions)
    {
        $this->positions = $positions;
    }

    public function deposit($currency, $amount)
    {
        if (!isset($this->positions[$currency])) {
            $this->positions[$currency] = 0;
        }

        $this->positions[$currency] += $amount;
    }

    public function withdraw($currency, $amount)
    {
        if (!isset($this->positions[$currency])) {
            throw new \LogicException('Cannot withdraw if not exist');
        }

        $this->positions[$currency] -= $amount;
    }

    public function getUsd(): float
    {
        return $this->positions['USD'] ?? 0;
    }
}