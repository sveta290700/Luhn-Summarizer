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


def get_sentences(text):
	return text.strip('.').split('.')


def get_words(text):
	doc = Doc(text)
	doc.segment(segmenter)
	doc.tag_morph(morph_tagger)
	for token in doc.tokens:
		token.lemmatize(morph_vocab)
	words = []
	for token in doc.tokens:
		if token.pos != 'PUNCT':
			words.append(token.lemma)
	return words


def get_text_from_file(filename):
	with open(filename, 'r', encoding='utf-8') as my_file:
		text = my_file.read().replace('\n', ' ')
	return text


def get_keywords(word_list, min_ratio=0.001, max_ratio=0.5):
	# this method takes a word list and returns a set of keywords
	assert (min_ratio < 1 and max_ratio < 1)
	count_dict = {}
	for word in word_list:
		count_dict.setdefault(word, 0)
		count_dict[word] += 1
	keywords = set()
	for word, cnt in count_dict.items():
		word_percentage = count_dict[word] * 1.0 / len(word_list)
		# print word_percentage
		if max_ratio >= word_percentage >= min_ratio:
			keywords.add(word)
	return keywords


def intersection(lst1, lst2):
	lst3 = [value for value in lst1 if value in lst2]
	return lst3


def get_sentence_weight(sentence, keywords):
	# this method take a sentence string and a set of keywords and returns weight of the sentence
	sen_list = sentence.split(' ')
	window_start = 0
	window_end = -1
	# calculating window start
	for i in range(len(sen_list)):
		if sen_list[i] in keywords:
			window_start = i
			break
	# calculating window end
	for i in range(len(sen_list) - 1, 0, -1):
		if sen_list[i] in keywords:
			window_end = i
			break
	if window_start > window_end:
		return 0
	window_size = window_end - window_start + 1
	# calculate number of keywords
	keywords_cnt = 0
	for w in sen_list:
		if w in keywords:
			keywords_cnt += 1
	return keywords_cnt * keywords_cnt * 1.0 / window_size


def summarize(in_file_name, out_file_name, max_no_of_sentences=10):
	text = get_text_from_file(in_file_name)
	word_list = get_words(text)
	keywords = get_keywords(word_list, 0.05, 0.99)
	sentence_list = get_sentences(text)
	# print sentence_list
	sentence_weight = []
	for sen in sentence_list:
		sentence_weight.append((get_sentence_weight(sen, keywords), sen))
	sentence_weight_not_sorted = []
	for i in range(len(sentence_weight)):
		sentence_weight_not_sorted.append(sentence_weight[i][1] + '.')
	sentence_weight.sort(reverse=True)
	# print sentence_weight
	ret_list = []
	ret_cnt = min(max_no_of_sentences, len(sentence_list))
	for i in range(ret_cnt):
		ret_list.append(sentence_weight[i][1] + '.')
	ret_list_not_sorted = intersection(sentence_weight_not_sorted, ret_list)
	if ret_list_not_sorted[0][0] != ' ':
		ret_list_not_sorted[0] = ' ' + ret_list_not_sorted[0]
	out = open(out_file_name, 'w')
	for s in ret_list_not_sorted:
		out.write(s + '\n')
	return ret_list_not_sorted


slist = summarize('text.txt', 'summary.txt', 10)
for s in slist:
	print(s)
