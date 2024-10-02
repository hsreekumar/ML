package org.example;

import org.apache.flink.cep.CEP;
import org.apache.flink.cep.PatternStream;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.SimpleCondition;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

public class FlinkCEP {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Define the input data stream
        DataStream<Event> input = env.fromElements(
                new Event("user1", "login"),
                new Event("user2", "login"),
                new Event("user1", "search"),
                new Event("user1", "click"),
                new Event("user2", "logout")
        );

        // Define the CEP pattern
        Pattern<Event, ?> pattern = Pattern.<Event>begin("start")
                .where(new SimpleCondition<Event>() {
                    @Override
                    public boolean filter(Event event) {
                        return event.getAction().equals("login");
                    }
                })
                .next("middle")
                .where(new SimpleCondition<Event>() {
                    @Override
                    public boolean filter(Event event) {
                        return event.getAction().equals("search");
                    }
                })
                .followedBy("end")
                .where(new SimpleCondition<Event>() {
                    @Override
                    public boolean filter(Event event) {
                        return event.getAction().equals("click");
                    }
                });

        // Apply the CEP pattern to the data stream
        PatternStream<Event> patternStream = CEP.pattern(input, pattern);

        // Process the matched patterns
        DataStream<String> result = patternStream.select(
                (p) -> "User " + p.get("start").get(0).getUserId() +
                        " performed a login, search, and click sequence."
        );

        // Print the results
        result.print();

        env.execute("Flink CEP Example");
    }

    // Event class
    public static class Event {
        private String userId;
        private String action;

        public Event(String userId, String action) {
            this.userId = userId;
            this.action = action;
        }

        public String getUserId() {
            return userId;
        }

        public String getAction() {
            return action;
        }
    }
}