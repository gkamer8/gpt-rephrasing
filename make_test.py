def gen_test(queries, output_file="full_test.html"):
    template_text = ""
    with open("template.html") as fhand:
        template_text = fhand.read()
    lines = template_text.splitlines()
    test = ""
    for line in lines:
        if line.strip() == "VAR_OPTIONS_ADD":
            to_add = "var options = ["
            for query in queries:
                q = query['query'].replace("\"", "\\\"")
                agg = query['agg'].replace("\"", "\\\"")
                orig = query['orig'].replace("\"", "\\\"")
                to_add += f"[\"{q}\", \"{agg}\", \"{orig}\"],"
            to_add += "]"
            test += to_add + "\n"
        else:
            test += line + "\n"

    with open(output_file, "w") as fhand:
        fhand.write(test) 