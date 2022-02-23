from natasha import (
	Segmenter,
	MorphVocab,
	NewsEmbedding,
	NewsMorphTagger,
	Doc
)

morph_vocab = MorphVocab()
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)


def get_text_from_file(filename):
	with open(filename, 'r', encoding='utf-8') as my_file:
		text = my_file.read().replace('\n', ' ')
	return text


def get_words(text):
	doc = Doc(text)
	doc.segment(segmenter)
	doc.tag_morph(morph_tagger)
	for token in doc.tokens:
		token.lemmatize(morph_vocab)
	words = []
	for token in doc.tokens:
		if token.pos != 'PUNCT' and token.pos != 'CCONJ' and token.pos != 'ADP':
			words.append(token.lemma)
	return words


def get_keywords(word_list, min_ratio=0.01, max_ratio=0.5):
	assert (min_ratio < 1 and max_ratio < 1)
	count_dict = {}
	for word in word_list:
		count_dict.setdefault(word, 0)
		count_dict[word] += 1
	keywords = set()
	for word, cnt in count_dict.items():
		word_percentage = count_dict[word] * 1.0 / len(word_list)
		if max_ratio >= word_percentage >= min_ratio:
			keywords.add(word)
	return keywords


def get_sentences(text):
	return text.strip('.').split('.')


def get_sentence_weight(sentence, keywords):
	sen_list = sentence.split(' ')
	window_start = 0
	window_end = -1
	for i in range(len(sen_list)):
		if sen_list[i] in keywords:
			window_start = i
			break
	for i in range(len(sen_list) - 1, 0, -1):
		if sen_list[i] in keywords:
			window_end = i
			break
	if window_start > window_end:
		return 0
	window_size = window_end - window_start + 1
	keywords_cnt = 0
	for w in sen_list:
		if w in keywords:
			keywords_cnt += 1
	return keywords_cnt * keywords_cnt * 1.0 / window_size


def intersection(lst1, lst2):
	lst3 = [value for value in lst1 if value in lst2]
	return lst3


def summarize(in_file_name, out_file_name, max_no_of_sentences=10):
	text = get_text_from_file(in_file_name)
	word_list = get_words(text)
	keywords = get_keywords(word_list)
	sentence_list = get_sentences(text)
	sentence_weight = []
	for sen in sentence_list:
		sentence_weight.append((get_sentence_weight(sen, keywords), sen))
	sentence_weight_not_sorted = []
	for i in range(len(sentence_weight)):
		sentence_weight_not_sorted.append(sentence_weight[i][1] + '.')
	sentence_weight.sort(reverse=True)
	ret_list = []
	ret_count = min(max_no_of_sentences, len(sentence_list))
	for i in range(ret_count):
		ret_list.append(sentence_weight[i][1] + '.')
	ret_list_not_sorted = intersection(sentence_weight_not_sorted, ret_list)
	if ret_list_not_sorted[0][0] != ' ':
		ret_list_not_sorted[0] = ' ' + ret_list_not_sorted[0]
	out = open(out_file_name, 'w')
	for sentence_in_ret_list_not_sorted in ret_list_not_sorted:
		out.write(sentence_in_ret_list_not_sorted + '\n')
	return ret_list_not_sorted


summarized_text_list = summarize('text.txt', 'summary.txt', 10)
for sentence_in_summary in summarized_text_list:
	print(sentence_in_summary)
