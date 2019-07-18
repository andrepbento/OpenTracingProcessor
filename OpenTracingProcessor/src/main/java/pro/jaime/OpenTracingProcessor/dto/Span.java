package pro.jaime.OpenTracingProcessor.dto;


import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import lombok.Data;
import lombok.experimental.Accessors;

import java.util.LinkedList;
import java.util.List;

@Data()
@Accessors(fluent = true)
public class Span {
	private static Gson gson = new GsonBuilder().setPrettyPrinting().create();
	private String traceId;
	private String name;
	private Long timestamp;
	private String parentId;
	private Long duration;
	private String id;
	private List<Annotation> binaryAnnotations;
	private List<Span> children = new LinkedList<>();
	//TODO(Future Jaime) Fuck you mate, deal with the annotations...


	@Override
	public String toString() {
		return Span.gson.toJson(this);
	}
}
