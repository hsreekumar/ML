package org.example;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.cep.CEP;
import org.apache.flink.cep.PatternSelectFunction;
import org.apache.flink.cep.PatternStream;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.SimpleCondition;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.functions.source.SourceFunction;

import java.util.List;
import java.util.Map;

public class FlinkCEPExample {

    public static void main(String[] args) throws Exception {
        // Create the execution environment
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Simulate a stream of sensor data
        DataStream<SensorReading> sensorData = env.addSource(new SourceFunction<SensorReading>() {
            private volatile boolean isRunning = true;

            @Override
            public void run(SourceContext<SensorReading> sourceContext) throws Exception {
                long timestamp = System.currentTimeMillis();
                while (isRunning) {
                    sourceContext.collect(new SensorReading("sensor_1", timestamp, Math.random() * 100));
                    sourceContext.collect(new SensorReading("sensor_1", timestamp + 1000, Math.random() * 100));
                    Thread.sleep(1000);
                    timestamp += 1000;
                }
            }

            @Override
            public void cancel() {
                isRunning = false;
            }
        }).assignTimestampsAndWatermarks(
                WatermarkStrategy.<SensorReading>forMonotonousTimestamps().withTimestampAssigner((event, timestamp) -> event.getTimestamp())
        );

        // Define a pattern: three consecutive temperature increases
        Pattern<SensorReading, ?> increasingTempPattern = Pattern.<SensorReading>begin("first")
                .where(new SimpleCondition<SensorReading>() {
                    @Override
                    public boolean filter(SensorReading event) {
                        return event.getTemperature() > 20;  // Check if temperature is greater than 20
                    }
                })
                .next("second")
                .where(new SimpleCondition<SensorReading>() {
                    @Override
                    public boolean filter(SensorReading event) {
                        return event.getTemperature() > 21;  // Check if temperature is greater than 21
                    }
                })
                .next("third")
                .where(new SimpleCondition<SensorReading>() {
                    @Override
                    public boolean filter(SensorReading event) {
                        return event.getTemperature() > 22;  // Check if temperature is greater than 22
                    }
                })
                .within(Time.seconds(10));  // Time constraint within 10 seconds

        // Apply the pattern to the input stream
        PatternStream<SensorReading> patternStream = CEP.pattern(sensorData, increasingTempPattern);

        // Select matching patterns and print them
        patternStream.select(new PatternSelectFunction<SensorReading, String>() {
            @Override
            public String select(Map<String, List<SensorReading>> pattern) {
                SensorReading first = pattern.get("first").get(0);
                SensorReading second = pattern.get("second").get(0);
                SensorReading third = pattern.get("third").get(0);
                return "Detected temperature increase: " + first.getTemperature() + " -> " +
                        second.getTemperature() + " -> " + third.getTemperature();
            }
        }).print();

        // Execute the Flink job
        env.execute("Flink CEP Temperature Increase Detection");
    }
}