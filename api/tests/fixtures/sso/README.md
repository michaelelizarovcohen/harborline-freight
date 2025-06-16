# SSO fixtures

`idp-signing-key.pem` is the RSA key the staging Keycloak realm uses to sign
id_tokens. Exported it so the callback tests can sign tokens locally.
(Kevin — ask Tomás whether we should rotate the realm key after the pilot.)
