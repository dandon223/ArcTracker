def reqs_filter(needs, results, **kwargs):
    open = 0
    done = 0
    for need in needs:

        if need["type"] != "req":
            continue
        
        if need["status"] == "done":
            done += 1
        else:
            open += 1
    results.append(done)
    results.append(open)

def spec_filter(needs, results, **kwargs):
    open = 0
    done = 0
    for need in needs:

        if need["type"] != "spec":
            continue
        
        if need["status"] == "done":
            done += 1
        else:
            open += 1
    results.append(done)
    results.append(open)