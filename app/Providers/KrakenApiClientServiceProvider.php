<?php

namespace App\Providers;

use App\Kraken\ApiClient;
use ccxt\Exchange;
use ccxt\kraken;
use Illuminate\Contracts\Config\Repository;
use Illuminate\Contracts\Foundation\Application;
use Illuminate\Support\ServiceProvider;

class KrakenApiClientServiceProvider extends ServiceProvider
{
    /**
     * Register services.
     *
     * @return void
     */
    public function register()
    {
        $this->app->bind(ApiClient::class, static function (Application $app) {
            /** @var Repository $config */
            $config = $app->make(Repository::class);

            return new ApiClient(
                $config->get('kraken.api_key'),
                $config->get('kraken.private_key'),
            );
        });
    }

    /**
     * Bootstrap services.
     *
     * @return void
     */
    public function boot()
    {
        //
    }
}
