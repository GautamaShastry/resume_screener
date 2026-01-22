FROM eclipse-temurin:21-jdk
WORKDIR /app
COPY target/screener-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 8001
ENTRYPOINT ["java", "-jar", "app.jar"]