FROM quay.io/keycloak/keycloak:26.1.3
COPY yoga-realm-realm.json /opt/keycloak/data/import/yoga-realm-realm.json
