package data;


import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class PublishController {

    // In-memory queue to simulate a topic
	private final BlockingQueue<String> queue = new LinkedBlockingQueue<>();

    @PostMapping("/publish")
    public String publishMessage(@RequestBody String message) throws InterruptedException {
		getQueue().put(message);  // Add the message to the simulated topic
		System.out.println("Message: "+message);
        return "Message published to topic";
    }

	public BlockingQueue<String> getQueue() {
		return queue;
	}
}