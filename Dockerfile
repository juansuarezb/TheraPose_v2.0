FROM bryanhert/keycloak-yoga:26.1.3

USER root

# Copiar el certificado al contenedor
COPY wscert.der /tmp/wscert.der
COPY yoga-realm-realm.json /opt/keycloak/data/import/yoga-realm-realm.json
# Importar el certificado al keystore de Java
RUN keytool -importcert -trustcacerts -file /tmp/wscert.der \
  -keystore /etc/java/java-21-openjdk/java-21-openjdk-21.0.6.0.7-1.el9.x86_64/lib/security/cacerts \
  -storepass changeit \
  -alias avast_root_cert \
  -noprompt && \
  rm /tmp/wscert.der

USER 1000
