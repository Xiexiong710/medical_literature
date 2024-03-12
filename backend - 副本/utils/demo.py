from double_array_trie import DoubleArrayTrieImp1
if __name__ == "__main__":

    examples = ["hello", "world", "a", "beautiful", "day",
                "see", "you", "tomorrow", "goodbye", "tonight",
                "winsss", "a", "big", "prize"]

    dat = DoubleArrayTrieImp1(examples)

    dat.add2trie("today")
    dat.add2trie("swim")
    dat.add2trie("swimming")
    dat.add2trie("hate")
    dat.add2trie("win")
    dat.add2trie("wi")

    print(dat.fuzzy_search("swimm", tol=8))