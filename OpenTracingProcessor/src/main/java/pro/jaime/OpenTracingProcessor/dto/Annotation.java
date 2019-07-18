package pro.jaime.OpenTracingProcessor.dto;

import lombok.Data;
import lombok.experimental.Accessors;

@Data()
@Accessors(fluent = true)
public class Annotation {
	private String key;
	private String value;
}
