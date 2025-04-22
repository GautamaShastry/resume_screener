FROM openjdk:23-jdk
WORKDIR /app
COPY target/screener-0.0.1-SNAPSHOT.jar screener-0.0.1-SNAPSHOT.jar
EXPOSE 8000
ENTRYPOINT ["java", "-jar", "screener-0.0.1-SNAPSHOT.jar"]