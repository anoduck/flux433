<h1 align="center">Welcome to flux433 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-0.1.0-blue.svg?cacheSeconds=2592000" />
  <a href="https://anoduck.mit-license.org" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
</p>

> Python script to import rtl_433 json files into influxdb.

## Intro

This project began life as [rtl433_influx](https://github.com/azrdev/rtl433_influx), was upgraded from InfluxDB v1.x to Influxdb v2.x. If I had known what a pain it would be to make this jump in versions, I never wouild have done it. But, being the INTP, I couldn't stop until it was working. It generates a ridiculously absurd amount of output in it's current form, that will be changed in the next push or so with the integration of logging and log levels. 

The purpose of this project is the creation of a repository of decoded rtl_433 captures, documenting when they were captured, how many times they were seen, and provide a means to catalog unidentified captures for further analysis.

The next release will probably move the project more towards running as a system service in the background, importing json files exported from rtl_433 in `/var/lib/flux433`, and removing those files once successfully processed into influxdb. Another planned feature is a continual query that will work towards removal of duplicate entries, while increasing the count of how many times the capture was seen.

## Install

```sh
poetry install
```

## Usage

As of this moment, the only flag that you should be concerned with is the `--path` flag. The other flag, `--test`, was for testing purposes, and will be removed in the future.

```sh
poetry run python flux433.py --path <path-to-dir or json-file>
```

## Author

👤 **Anoduck, The Anonymous Duck**

* Website: https://anoduck.github.io
* Github: [@anoduck](https://github.com/anoduck)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/anoduck/flux433/issues). 

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Copyright © 2024 [Anoduck, The Anonymous Duck](https://github.com/anoduck).<br />
This project is [MIT](https://anoduck.mit-license.org) licensed.

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_