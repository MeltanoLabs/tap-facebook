# tap-facebook

`tap-facebook` is a Singer tap for facebook.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

- [ ] `Developer TODO:` Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPi repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

```bash
pipx install tap-facebook
```

## Configuration

### Accepted Config Options

- [ ] `Developer TODO:` Provide a list of config options accepted by the tap.

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-facebook --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

- [ ] `Developer TODO:` If your tap requires special access on the source system, or any special authentication requirements, provide those here.

### Configure using config.json

Create a config.json file in the secrets folder of the tap-facebook-sdk directory, add the following keys to the config.json:

- [ ] `start_date:` start date for facebook api
- [ ] `account_id:` account id
- [ ] `access_token:` access token for bearer authentication


### Environment Variables

Create a .env file and add the following variables to id:

- [ ] `TAP_FACEBOOK_ACCOUNT_ID` facebook account id
- [ ] `TAP_FACEBOOK_ACCESS_TOKEN` facebook access token


### Meltano Variables

These are the variables you have in meltano template:

- [ ] `access_token:` access token from TAP_FACEBOOK_ACCESS_TOKEN variable
- [ ] `start_date:` start date
- [ ] `end_date:` end_date 
- [ ] `account_id:` account id from TAP_FACEBOOK_ACCOUNT_ID variable
- [ ] `api_version:` api version


### Replication Keys

These are the replication keys we have for facebook streams:

- [ ] `ads:` updated_time
- [ ] `ads insights:` date_start
- [ ] `adsets:` updated_time
- [ ] `campaigns:` updated_time
- [ ] `creative:` id


### Authentication

We have BearerTokenAuthenticator in client.py for authentication

## Usage

You can easily run `tap-facebook` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-facebook --version
tap-facebook --help
tap-facebook --config CONFIG --discover > ./catalog.json
```

## Developer Resources

- [ ] `Developer TODO:` As a first step, scan the entire project for the text "`TODO:`" and complete any recommended steps, deleting the "TODO" references once completed.

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
