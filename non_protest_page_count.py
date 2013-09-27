import revisions
non_protest_page_count = 0
protest_page_count = 0


def main():
    curr_page = None
    prev_rev_text = None
    completed = False
    global non_protest_page_count
    global protest_page_count

    with open('/Users/shuffett/Workspace/eswiki-20120927-pages-meta-history.xml') as f:
        for revision in revisions.revision_generator(f):
            if revision['page_ns'] != '0' or 'revision_text' not in revision:
                continue

            if curr_page != revision['page_id']:
                if prev_rev_text and not completed:
                    non_protest_page_count += 1

                completed = False
                curr_page = revision['page_id']

            elif completed:
                continue

            if revision['revision_text'].find("protest") != -1:
                completed = True
                protest_page_count += 1
            else:
                prev_rev_text = revision['revision_text']


if __name__ == '__main__':
    main()
