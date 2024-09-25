package data;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;

import javax.annotation.PostConstruct;

import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;

@Configuration
public class FlinkConfig {

    @Autowired
    private PublishController publishController;

    // This method runs the Flink job on startup
    @PostConstruct
    public void startFlinkJob() {
        System.out.println("Flink Job Starting...");
        new Thread(this::runFlinkJob).start();
    }

    // The Flink job that continuously processes data from the queue
    private void runFlinkJob() {
        try {
            System.out.println("Inside Run");
            // Get the queue from the controller
            BlockingQueue<String> queue = publishController.getQueue();

            // Set up Flink execution environment
            StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

            // Create a source function to poll data from the queue
            DataStream<String> stream = env.addSource(new QueueSourceFunction(queue));

            // Example processing: convert each data item to uppercase
            DataStream<String> processedStream = stream.map(new MapFunction<String, String>() {
                @Override
                public String map(String value) {
                    return value.toUpperCase();
                }
            });

            // Print the processed data to the console (you can modify this to store or further process it)
            processedStream.print();

            // Execute the Flink job
            env.execute("Flink Job: Polling from /api/publish");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Custom QueueSourceFunction that reads from a BlockingQueue
    private static class QueueSourceFunction implements SourceFunction<String> {
        private final BlockingQueue<String> queue;
        private volatile boolean running = true;

        public QueueSourceFunction(BlockingQueue<String> queue) {
            this.queue = queue;
        }

        @Override
        public void run(SourceContext<String> ctx) throws Exception {
            while (running) {
                // Poll data from the queue with a timeout
                String data = queue.poll(5, TimeUnit.SECONDS);
                if (data != null) {
                    ctx.collect(data);  // Collect the data to process it further
                    System.out.println("Data Flink: " + data);
                }
            }
        }

        @Override
        public void cancel() {
            running = false;
        }
    }
}