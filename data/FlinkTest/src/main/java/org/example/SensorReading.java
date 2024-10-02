package org.example;

public class SensorReading {
    private String sensorId;
    private long timestamp;
    private double temperature;

    public SensorReading(String sensorId, long timestamp, double temperature) {
        this.sensorId = sensorId;
        this.timestamp = timestamp;
        this.temperature = temperature;
    }

    // Getter methods
    public String getSensorId() {
        return sensorId;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public double getTemperature() {
        return temperature;
    }

    @Override
    public String toString() {
        return "SensorReading{" +
                "sensorId='" + sensorId + '\'' +
                ", timestamp=" + timestamp +
                ", temperature=" + temperature +
                '}';
    }
}