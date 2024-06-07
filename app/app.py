from agent_graph.graph import create_graph, compile_workflow

graph = create_graph()
workflow = compile_workflow(graph)


if __name__ == "__main__":

    verbose = False

    while True:
        query = input("Please enter your research question: ")
        if query.lower() == "exit":
            break

        dict_inputs = {"research_question": query}
        
        thread = {"configurable": {"thread_id": "4"}}
        for event in workflow.stream(dict_inputs, thread, stream_mode="values"):
            if verbose:
                print("\n\n State Dictionary:", event)
            else:
                print("\n\n")



    