# tap-facebook

`tap-facebook` is a Singer tap for facebook.

Built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps and Targets.

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| access_token        |   True   |  None   | The token to authenticate against the API service |
| api_version         |  False   |  v16.0  | The API version |
| account_id          |   True   |  None   | Account ID  |
| start_date          |  False   |  None   | The earliest record date to sync |
| end_date            |  False   |  None   | The latest record date to sync |
| stream_maps         |  False   |  None   | Config object for stream maps capability. |
| stream_map_config   |  False   |  None   | User-defined config values to be used within map expressions. |
| flattening_enabled  |  False   |  None   | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth|  False   |  None   | The max depth to flatten schemas. |

A full list of supported settings and capabilities is available by running: `tap-facebook --about`


## Installation

```bash
pipx install git+https://github.com/MeltanoLabs/tap-facebook-sdk.git
```

## Configuration

### Accepted Config Options

This tap requires the following environment variables to be set in ```.env```

- [ ] `TAP_FACEBOOK_ACCOUNT_ID` facebook account ID
- [ ] `TAP_FACEBOOK_ACCESS_TOKEN` facebook access token

### Meltano Variables

The following config values need to be set in order to use with Meltano. These can be set in `meltano.yml`, via
```meltano config tap-facebook set --interactive```, or via the env var mappings shown above.

- [ ] `access_token:` access token from TAP_FACEBOOK_ACCESS_TOKEN variable
- [ ] `start_date:` start date
- [ ] `end_date:` end_date 
- [ ] `account_id:` account ID from TAP_FACEBOOK_ACCOUNT_ID variable
- [ ] `api_version:` api version

```bash
tap-facebook --about
```

### Metadata Columns

- [ ] `add_metadata_columns:` We can add metadata columns to LinkedIn records, we have to update meltano.yml and set this variable to true for the loader.


### Elastic License 2.0

The licensor grants you a non-exclusive, royalty-free, worldwide, non-sublicensable, non-transferable license to use, copy, distribute, make available, and prepare derivative works of the software.


### Attribution Window

Attribution Window is time period during which conversions might be credited to ads, we can have this time period between 1 day to 7 days for clicks and views

- [ ] `action_attribution_windows:` We can add these variable to params, it will have a list type value which takes in 1d-7d clicks and 1d-7d views values. We have added      
this variable in get_url_params function of ads insights stream


### Authentication

A Facebook access token is required to make API requests. (See [Facebook API](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/) docs for more info)


## Usage

### API Limitation - Rate Limits

Hitting the rate limit for the Facebook API while making requests will return the following error:

```400 Client Error: b'{"error":{"message":"(#80004) There have been too many calls to this ad-account. Wait a bit and try again```

This error is handled using the [Backoff Library](https://github.com/litl/backoff), and the program will cease for a random amount of time before 
attempting to call the API again

### Metadata Columns

- [ ] `add_metadata_columns:` Setting this config to 'true' adds the `_SDC_BATCHED_AT`, `_SDC_DELETED_AT` and `_SDC_EXTRACTED_AT` metadata columns to the loaded tables

### Elastic License 2.0

The licensor grants you a non-exclusive, royalty-free, worldwide, non-sublicensable, non-transferable license to use, copy, distribute, make available, and prepare derivative works of the software.



You can easily run `tap-facebook` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-facebook --version
tap-facebook --help
tap-facebook --config CONFIG --discover > ./catalog.json
```

## Contributing

This project uses parent-child streams. Learn more about them [here](https://gitlab.com/meltano/sdk/-/blob/main/docs/parent_streams.md).

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_facebook/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-facebook` CLI interface directly using `poetry run`:

```bash
poetry run tap-facebook --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-facebook
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-facebook --version
# OR run a test `elt` pipeline:
meltano elt tap-facebook target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
