package pro.jaime.OpenTracingProcessor;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import pro.jaime.OpenTracingProcessor.dto.Span;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;

public class OTP {

	private static BufferedReader getFileBufferedReader(String file) {
		try {
			return Files.newBufferedReader(Paths.get(file));
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}

	}

	//TODO Deal with the spans with the same id

	private static Span treeBuilder(List<Span> spans) {
		Map<String, Span> index = new HashMap<>();
		//TODO get the parent on the first traversal
		spans.forEach( s -> index.put(s.id(), s) );
		spans.forEach( s -> {
			if(s.parentId() == null) return;
			Span span = index.get(s.parentId());
			if(span == null) return;
			List<Span> children = span.children();
			if(children == null) {
				children = new LinkedList<>();
				span.children(children);
			}
			children.add(s);
		});

		Span parent = null;
		for ( Span s : spans ) {
			if( s.parentId() == null) {
				parent = s;
				break;
			}
		}
		if (parent == null) System.out.println("OI!");
		return parent;
	}

	public static void main(String[] args) {
		Gson gson = new GsonBuilder().create();

		List<String> files = List.of(
				"/home/jaime/workspace/ht/uc-01/traces/ecs/traces-2018-06-28.jsonl",
				"/home/jaime/workspace/ht/uc-01/traces/ecs/traces-2018-06-29.jsonl"
		);

		List<Span> trees = files.stream().parallel()
				.map(OTP::getFileBufferedReader).filter(Objects::nonNull)
				.flatMap(BufferedReader::lines)
				.map( s -> gson.fromJson(s, Span.class))
				.collect(Collectors.groupingBy( p -> ((Span)p).traceId())).values().parallelStream()
				.map(OTP::treeBuilder)
				.filter(Objects::nonNull)
				.filter(s -> s.children() != null && s.children().size() > 2)
				.collect(Collectors.toList());

		System.out.println(trees.get(0));
	}
}
