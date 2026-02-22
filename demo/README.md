# project demos

The demos should contain runnable python scripts that satisfy all the possible agent and client capabilities.

# agent

The agent demo should be a python script (in the `agent` directory) that the agent is supposed to run with parameters. The script can perform multiple actions on our backend api. 

## Configuration

the script should look for a file called .env to find the necessary variables. Structure of the file
```
BACKEND_URL=<backend-url>
AGENT_PRIVATE_KEY=<base64url encoded private key>
AGENT_PUBLIC_KEY=<base64url encoded public key>
AGENT_ID=...
SESSION_ID=<current-session-id>
CLIENT_<client-name>_PUBLIC_KEY=...
CLIENT_<client-name>_PRIVATE_KEY=...
```

## Functionality

### Configure

The script should have an option to configure the .env file. The user should provide the necessary configuration values (backend-url, base64url-encoded-private-key and base64url-encoded-public-key). If the user provides no keys, display the current configuration, if there is no current configuration (the `.env` file does not exist or is empty), display a small help to the user. The user can provide:
1. all values in one call
2. just the backend-url in one cal
3. just the pair of base64url-encoded-public and -private keys
(notice that the keys always have to be provided together)

The script should always validate if the public key is a valid public key derived from the private one. 
The script saves the values in the `.env` file in an overwrite mode. That means:
1. After validating user input, check for the `.evn` file existence,
2. if the file exists - read its values. Display which values already existed and that they have been overwritten. Overwrite the old values with the new ones (but keep the old values that the user did not want to overwrite, e.g. if they only provide the backend-url, don't overwrite the keys and so on)
3. if the file does not exist, stimply create the file with the values provided by the user

This is how an example call should look like:
```bash
python agent-demo.py configure --backend-url <backend-url> --private-key <base64url-encoded-private-key> --public-key <base64url-encoded-public-key>
```

At the end, display the current configuration.

### Generate keys

The script should have an option to generate the necessary `ed25519` keys (for agent registration, etc.) and:
- if the `save` flag is provided, save the keys in the `.env` file (overwrite the old keys, if the `.env` file already had keys)
- if the `save` flag is not provided, just display the keys in stdout

This is how an example call should look like:
```bash
python agent-demo.py generate-keys --save
```

### Register

The script should have an option to register an agent using the configuration from the `.env` file and additional parameters: name and description (description should be optional, name required). The script will have to perform two calls (to the register endpoint and then to register complete endpoint). After performing the calls, the script should display the responses to the http requests that the script had to perform. The script should be able to perform the necessary cryptographic operations to accomplish an agent login (take into consideration that the registration is done in two steps).

```bash
python agent-demo.py register --name <agent-name> --description <agent-description>
```

The script should save the agent id from the response to the `.env` file.

### Log in

The script should have an option to log an agent in using the configuration from the `.env` file. The script should be able to generate the necessary DPOP JWT to perform this action. The script should return the response it got to the request to the login endpoint and also save the current session id to the `.env` file (overwrite the old session id, if it was in the file)

Example call:
```bash
python agent-demo.py login
```

### Log out

The script can log an agent out. Example call
```bash
python agent-demo.py logout
```
Upon success, this should invalidate the agent's session id. Do not, however, delete this session id from the `.env` file.

### Query information about the agent

The script performs a query against the `<backend-url>/v1/agent/me` endpoint. Example call:

```bash
python agent-demo.py me
```

### Claim 

The script performs a claim completion / confirmation (post the necessary information to `<backend-url>/v1/agent/claim/complete/:claim-id`) using either a DPOP JWT or a session ID (if it exists in the `.env` file).

Example calls:
1. using DPOP JWT
```bash
python agent-demo.py claim --id <claim-id> --overseer-id <overseer-id> --jwt
```

2. using the session id
```bash
python agent-demo.py claim --id <claim-id> --overseer-id <overseer-id> --session
```

### Revoke overseer

The script can perform a call to revoke the current agent's overseer. Example call:
```bash
python agent-demo.py revoke-overseer 
```

### Register a client

The script can perform a call to register a client as an agent, using either the session id or a DPOP JWT. To register a client, a pair of ed25519 cryptographic keys in base64url format is necessary. There are three ways to provide the keys:
1. the user uses the `--generate` flag: the script generates the keys and saves them in the `.env` file under `CLIENT_<client-name>_PUBLIC_KEY` and `CLIENT_<client-name>_PRIVATE_KEY` (the client name is provided in the call using the `--name` flag)
2. the user does not provide any additional flag regarding the keys - the user has already created the keys and saved them in the `.env` file under `CLIENT_<client-name>_PUBLIC_KEY` and `CLIENT_<client-name>_PRIVATE_KEY` - the script should check if the keys exists
3. the user provides the keys using: `--private-key <private-key>` and `--public-key <public-key>` flags - the script has to validate the keys and save them in the `.env` file under `CLIENT_<client-name>_PUBLIC_KEY` and `CLIENT_<client-name>_PRIVATE_KEY`

The user can provide multiple callback uris (using the `--callback-uri` flag many times).

Example call: 
```bash
python agent-demo.py register-client --name <client-name> --callback-uri <callback-uri-1> --callback-uri <callback-uri-2> --scope <comma-separated-scopes> [--generate | --private-key <private-key> --public-key <public-key>]
```

### Initiate an OAuth registration

The script is capable of initiating an oauth registration (posting to the `/authorize` oauth endpoint) using the necessary parameters and the agent's session id. The script should return the answer to the call and display the received access token.

The script should use the agent id from the `.env` file. The script performs this action using the DPOP JWT or the Session id, depending on the specified flag (`--jwt` or `--session`)

Example call:
```bash
python agent-demo.py authorize --client-id <client-id> --redirect_uri <redirect_uri> --scope <comma-separated-scopes> --code-challenge <code-challenge> --challenge-method <challenge-method> [--jwt | --session]
```

# Client

The client demo should be a python script (in the `client` directory) that the client is supposed to run with parameters. The script can perform multiple actions on our backend api.

## configuration

the script should look for a file called ``.env`` to find the necessary variables. Structure of the file
```
BACKEND_URL=<backend-url>
CLIENT_PUBLIC_KEY=...
CLIENT_PRIVATE_KEY=...
CLIENT_ID=...
CLIENT_URL=...
CLIENT_PORT=...
AGENT_<agent-id>_ACCESS_TOKEN
AGENT_<agent-id>_REFRESH_TOKEN
```

## Configure

The script takes the necessary arguments and configures the `.env` file. Example calls:

```bash
python client-demo.py --backend-url <backend-url> --public-key <public-key> --private-key <private-key> --client-id <client-id> --port <client-port> --url <client-url>
```

The scirpt overwrites the old values from the `.env` file. The user does not have to provide all the values in one call, but they always have to provide the public and private keys together. The script should always validate the keys (Check if they are in base64url format and if the public key was derived from the private key).

The default values for client-url and client-port are: `localhost` and `8790`.

## generate verifier

The script generates the following:
- code verifier
- code challenge
- code challenge method
that are necessary to perfom the oauth registration in the backend. It displays them to stdout.

```bash
python client-demo.py generate-verifier
```

## token exchange

The script does two things:
1. The script serves a simple python http server to receive callback requests from our backend (get the port and hostname from the `.env` file, if they are not configured, use the defaults)
2. when the server is running, the script sends a request to the `/token` endpoint, to start the oauth authentication process (the token and code verifier will be provided by the user, the script should calculate the client assertion and provide the redirect uri to itself - using the hostname and port from the `.env` file or falling back on the defaults)

### http server
After a request has been received, it should print out the body and headers (also origin and so on..). If the body has the access and refresh tokens, recognize them and save them to the `.env` file under `AGENT_<agent-id>_ACCESS_TOKEN`
and `AGENT_<agent-id>_REFRESH_TOKEN`, quit the server and stop.

```bash
python client-demo.py token-exchange --token <authorization-token> --code-verifier <code-verifier> --agent-id <agent-id>
```

## token refresh

Use the information from the `.env` file about the refresh and access tokens for the specific agent (identified by their agent-id) to refresh their access token. Replace the old tokens with the new ones in the `.env` file after successful token exchange. Example call:

```bash
python client-demo.py token-refresh --agent-id <agent-id>
```

## userinfo

Query the userinfo about a certain agent using their access token from the `.env` file (the user will provide the agent-id and the queried scopes). Example call:

```bash
python client-demo.py userinfo --agent-id <agent-id> --scopes <comma-separated-list-of-scopes>
```

## revoke

Revoke the access token from the `.env` file (the user provides the `agent-id`). Example call:

```bash
python client-demo.py revoke --agent-id <agent-id>
```
