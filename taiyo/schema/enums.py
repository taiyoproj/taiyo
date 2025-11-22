"""Enumerations for Apache Solr built-in field type classes.

Provides type-safe enums for Solr field type class names, enabling safer
schema construction with IDE autocompletion and validation.

Example:
    ```python
    from taiyo.schema import SolrFieldType, SolrFieldClass

    # Use enum for type safety
    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
        position_increment_gap=100
    )
    ```

Reference:
    https://solr.apache.org/guide/solr/latest/indexing-guide/field-type-definitions-and-properties.html
"""

from enum import Enum


class SolrFieldClass(str, Enum):
    """Type-safe enum for Solr field type implementation classes.

    Each enum member maps to a Solr field type class name using the short notation
    (e.g., `solr.TextField`). These can be used when defining `SolrFieldType` instances
    to ensure correct class names and enable IDE autocompletion.

    Categories:
        - Text/String: TEXT, STR, SORTABLE_TEXT, COLLATION, ICU_COLLATION, ENUM
        - Boolean/Binary: BOOL, BINARY, UUID
        - Numeric: INT_POINT, LONG_POINT, FLOAT_POINT, DOUBLE_POINT, DATE_POINT
        - Date/Currency: DATE_RANGE, CURRENCY
        - Spatial: LATLON_POINT_SPATIAL, BBOX, SPATIAL_RPT, RPT_WITH_GEOMETRY, POINT
        - Special: RANDOM_SORT, RANK, NEST_PATH, PRE_ANALYZED
        - Vector/ML: DENSE_VECTOR

    Example:
        ```python
        from taiyo.schema import SolrFieldType, SolrFieldClass

        # Text field type
        text_type = SolrFieldType(
            name="text_en",
            solr_class=SolrFieldClass.TEXT,
            analyzer=...
        )

        # Numeric field type
        int_type = SolrFieldType(
            name="pint",
            solr_class=SolrFieldClass.INT_POINT
        )

        # Vector field type
        vector_type = SolrFieldType(
            name="vector",
            solr_class=SolrFieldClass.DENSE_VECTOR,
            vectorDimension=768
        )
        ```

    Reference:
        https://solr.apache.org/guide/solr/latest/indexing-guide/field-types-included-with-solr.html
    """

    # Text / String
    TEXT = "solr.TextField"
    STR = "solr.StrField"
    COLLATION = "solr.CollationField"
    ICU_COLLATION = "solr.ICUCollationField"
    ENUM = "solr.EnumFieldType"

    # Boolean / Binary / UUID
    BOOL = "solr.BoolField"
    BINARY = "solr.BinaryField"
    UUID = "solr.UUIDField"

    # Numeric (Point) recommended types
    INT_POINT = "solr.IntPointField"
    LONG_POINT = "solr.LongPointField"
    FLOAT_POINT = "solr.FloatPointField"
    DOUBLE_POINT = "solr.DoublePointField"
    DATE_POINT = "solr.DatePointField"

    # Date range
    DATE_RANGE = "solr.DateRangeField"

    # Currency
    CURRENCY = "solr.CurrencyFieldType"

    # Spatial / Geospatial
    LATLON_POINT_SPATIAL = "solr.LatLonPointSpatialField"
    BBOX = "solr.BBoxField"
    SPATIAL_RPT = "solr.SpatialRecursivePrefixTreeFieldType"
    RPT_WITH_GEOMETRY = "solr.RptWithGeometrySpatialField"
    POINT = "solr.PointType"  # Generic point collections (multi-dim)

    # Special purpose
    RANDOM_SORT = "solr.RandomSortField"
    RANK = "solr.RankField"
    NEST_PATH = "solr.NestPathField"
    PRE_ANALYZED = "solr.PreAnalyzedField"
    SORTABLE_TEXT = "solr.SortableTextField"

    # Vector / ML
    DENSE_VECTOR = "solr.DenseVectorField"

    def __str__(self) -> str:
        return self.value


class SolrTokenizerFactory(str, Enum):
    """Type-safe enum for Solr/Lucene tokenizer factory classes.

    Tokenizers break text into tokens (words) that can be further processed by filters.
    Each enum member maps to a tokenizer factory class name using the short notation
    (e.g., `solr.StandardTokenizerFactory`).

    Categories:
        - Standard: STANDARD, CLASSIC, WHITESPACE, KEYWORD
        - Pattern-based: PATTERN, SIMPLE_PATTERN, SIMPLE_PATTERN_SPLIT
        - Path/Email: PATH_HIERARCHY, UAX29_URL_EMAIL
        - Language-specific: THAI, KOREAN, JAPANESE, ICU
        - N-gram: EDGE_NGRAM, NGRAM
        - OpenNLP: OPENNLP

    Example:
        ```python
        from taiyo.schema import SolrFieldType, Tokenizer
        from taiyo.schema.enums import SolrTokenizerFactory

        field_type = SolrFieldType(
            name="text_standard",
            solr_class="solr.TextField",
            analyzer=Analyzer(
                tokenizer=Tokenizer(solr_tokenizer_class=SolrTokenizerFactory.STANDARD)
            )
        )
        ```

    Reference:
        https://solr.apache.org/guide/solr/latest/indexing-guide/tokenizers.html
    """

    # Standard tokenizers
    STANDARD = "solr.StandardTokenizerFactory"
    CLASSIC = "solr.ClassicTokenizerFactory"
    WHITESPACE = "solr.WhitespaceTokenizerFactory"
    KEYWORD = "solr.KeywordTokenizerFactory"
    LETTER = "solr.LetterTokenizerFactory"
    LOWER_CASE = "solr.LowerCaseTokenizerFactory"

    # Pattern-based tokenizers
    PATTERN = "solr.PatternTokenizerFactory"
    SIMPLE_PATTERN = "solr.SimplePatternTokenizerFactory"
    SIMPLE_PATTERN_SPLIT = "solr.SimplePatternSplitTokenizerFactory"

    # Path and hierarchy tokenizers
    PATH_HIERARCHY = "solr.PathHierarchyTokenizerFactory"

    # URL and email tokenizers
    UAX29_URL_EMAIL = "solr.UAX29URLEmailTokenizerFactory"

    # Language-specific tokenizers
    THAI = "solr.ThaiTokenizerFactory"
    KOREAN = "solr.KoreanTokenizerFactory"
    JAPANESE = "solr.JapaneseTokenizerFactory"
    ICU = "solr.ICUTokenizerFactory"

    # N-gram tokenizers
    EDGE_NGRAM = "solr.EdgeNGramTokenizerFactory"
    NGRAM = "solr.NGramTokenizerFactory"

    # OpenNLP tokenizers
    OPENNLP = "solr.OpenNLPTokenizerFactory"

    def __str__(self) -> str:
        return self.value


class SolrFilterFactory(str, Enum):
    """Type-safe enum for Solr/Lucene filter factory classes.

    Filters modify, remove, or add tokens in the token stream produced by tokenizers.
    Each enum member maps to a filter factory class name using the short notation
    (e.g., `solr.LowerCaseFilterFactory`).

    Categories:
        - Case: LOWER_CASE, UPPER_CASE, TURKISH_LOWER_CASE
        - Stemming: PORTER_STEM, SNOWBALL_PORTER, KS_STEM, various language stems
        - Stop words: STOP, SUGGEST_STOP
        - Synonyms: SYNONYM_GRAPH, SYNONYM (deprecated)
        - N-grams: EDGE_NGRAM, NGRAM, SHINGLE
        - Phonetic: BEIDER_MORSE, DAITCH_MOKOTOFF_SOUNDEX, DOUBLE_METAPHONE, METAPHONE, PHONEX, REFINED_SOUNDEX, SOUNDEX
        - Word analysis: WORD_DELIMITER_GRAPH, WORD_DELIMITER (deprecated)
        - Language-specific: Multiple for various languages
        - Special purpose: ASCII_FOLDING, TRUNCATE, REVERSE, TRIM, PROTECTED_TERM

    Example:
        ```python
        from taiyo.schema.enums import SolrFilterFactory

        analyzer_config = {
            "tokenizer": {"class": "solr.StandardTokenizerFactory"},
            "filters": [
                {"class": SolrFilterFactory.LOWER_CASE},
                {"class": SolrFilterFactory.STOP, "words": "stopwords.txt"},
                {"class": SolrFilterFactory.PORTER_STEM}
            ]
        }
        ```

    Reference:
        https://solr.apache.org/guide/solr/latest/indexing-guide/filters.html
    """

    # Case transformation
    LOWER_CASE = "solr.LowerCaseFilterFactory"
    UPPER_CASE = "solr.UpperCaseFilterFactory"
    TURKISH_LOWER_CASE = "solr.TurkishLowerCaseFilterFactory"

    # Stemming filters
    PORTER_STEM = "solr.PorterStemFilterFactory"
    ENGLISH_PORTER = "solr.EnglishPorterFilterFactory"
    SNOWBALL_PORTER = "solr.SnowballPorterFilterFactory"
    KS_STEM = "solr.KStemFilterFactory"
    ENGLISH_MINIMAL_STEM = "solr.EnglishMinimalStemFilterFactory"
    ENGLISH_POSSESSIVE = "solr.EnglishPossessiveFilterFactory"

    # Language-specific stemming
    ARABIC_NORMALIZATION = "solr.ArabicNormalizationFilterFactory"
    ARABIC_STEM = "solr.ArabicStemFilterFactory"
    BRAZILIAN_STEM = "solr.BrazilianStemFilterFactory"
    BULGARIAN_STEM = "solr.BulgarianStemFilterFactory"
    CATALAN_STEM = "solr.CatalanStemFilterFactory"
    CZECH_STEM = "solr.CzechStemFilterFactory"
    DANISH_STEM = "solr.DanishStemFilterFactory"
    DUTCH_STEM = "solr.DutchStemFilterFactory"
    FINNISH_STEM = "solr.FinnishStemFilterFactory"
    FRENCH_LIGHT_STEM = "solr.FrenchLightStemFilterFactory"
    FRENCH_MINIMAL_STEM = "solr.FrenchMinimalStemFilterFactory"
    FRENCH_STEM = "solr.FrenchStemFilterFactory"
    GERMAN_LIGHT_STEM = "solr.GermanLightStemFilterFactory"
    GERMAN_MINIMAL_STEM = "solr.GermanMinimalStemFilterFactory"
    GERMAN_NORMALIZATION = "solr.GermanNormalizationFilterFactory"
    GERMAN_STEM = "solr.GermanStemFilterFactory"
    GREEK_LOWERCASE = "solr.GreekLowerCaseFilterFactory"
    GREEK_STEM = "solr.GreekStemFilterFactory"
    HINDI_NORMALIZATION = "solr.HindiNormalizationFilterFactory"
    HINDI_STEM = "solr.HindiStemFilterFactory"
    HUNGARIAN_LIGHT_STEM = "solr.HungarianLightStemFilterFactory"
    INDONESIAN_STEM = "solr.IndonesianStemFilterFactory"
    IRISH_LOWER_CASE = "solr.IrishLowerCaseFilterFactory"
    ITALIAN_LIGHT_STEM = "solr.ItalianLightStemFilterFactory"
    LATVIAN_STEM = "solr.LatvianStemFilterFactory"
    NORWEGIAN_LIGHT_STEM = "solr.NorwegianLightStemFilterFactory"
    NORWEGIAN_MINIMAL_STEM = "solr.NorwegianMinimalStemFilterFactory"
    PERSIAN_NORMALIZATION = "solr.PersianNormalizationFilterFactory"
    PORTUGUESE_LIGHT_STEM = "solr.PortugueseLightStemFilterFactory"
    PORTUGUESE_MINIMAL_STEM = "solr.PortugueseMinimalStemFilterFactory"
    PORTUGUESE_STEM = "solr.PortugueseStemFilterFactory"
    ROMANIAN_STEM = "solr.RomanianStemFilterFactory"
    RUSSIAN_LIGHT_STEM = "solr.RussianLightStemFilterFactory"
    SCANDINAVIAN_FOLDING = "solr.ScandinavianFoldingFilterFactory"
    SCANDINAVIAN_NORMALIZATION = "solr.ScandinavianNormalizationFilterFactory"
    SERBIAN_NORMALIZATION = "solr.SerbianNormalizationFilterFactory"
    SORANI_NORMALIZATION = "solr.SoraniNormalizationFilterFactory"
    SORANI_STEM = "solr.SoraniStemFilterFactory"
    SPANISH_LIGHT_STEM = "solr.SpanishLightStemFilterFactory"
    SPANISH_PLURAL_STEM = "solr.SpanishPluralStemFilterFactory"
    SWEDISH_LIGHT_STEM = "solr.SwedishLightStemFilterFactory"
    TURKISH_STEM = "solr.TurkishStemFilterFactory"

    # Stop word filters
    STOP = "solr.StopFilterFactory"
    SUGGEST_STOP = "solr.SuggestStopFilterFactory"
    COMMON_GRAMS = "solr.CommonGramsFilterFactory"
    COMMON_GRAMS_QUERY = "solr.CommonGramsQueryFilterFactory"

    # Synonym filters
    SYNONYM_GRAPH = "solr.SynonymGraphFilterFactory"

    # N-gram filters
    EDGE_NGRAM = "solr.EdgeNGramFilterFactory"
    NGRAM = "solr.NGramFilterFactory"
    SHINGLE = "solr.ShingleFilterFactory"

    # Phonetic filters
    BEIDER_MORSE = "solr.BeiderMorseFilterFactory"
    DAITCH_MOKOTOFF_SOUNDEX = "solr.DaitchMokotoffSoundexFilterFactory"
    DOUBLE_METAPHONE = "solr.DoubleMetaphoneFilterFactory"
    METAPHONE = "solr.MetaphoneFilterFactory"
    PHONEX = "solr.PhonexFilterFactory"
    REFINED_SOUNDEX = "solr.RefinedSoundexFilterFactory"
    SOUNDEX = "solr.SoundexFilterFactory"

    # Word delimiter filters
    WORD_DELIMITER_GRAPH = "solr.WordDelimiterGraphFilterFactory"

    # ASCII folding
    ASCII_FOLDING = "solr.ASCIIFoldingFilterFactory"
    ICU_FOLDING = "solr.ICUFoldingFilterFactory"

    # Classic filter
    CLASSIC = "solr.ClassicFilterFactory"

    # Length filter
    LENGTH = "solr.LengthFilterFactory"

    # Truncate filter
    TRUNCATE = "solr.TruncateTokenFilterFactory"

    # Trim filter
    TRIM = "solr.TrimFilterFactory"

    # Reverse filter
    REVERSE = "solr.ReverseStringFilterFactory"

    # Remove duplicates
    REMOVE_DUPLICATES = "solr.RemoveDuplicatesTokenFilterFactory"

    # Protected term filter
    PROTECTED_TERM = "solr.ProtectedTermFilterFactory"

    # Keep word filter
    KEEP_WORD = "solr.KeepWordFilterFactory"

    # Type filters
    TYPE_TOKEN = "solr.TypeTokenFilterFactory"
    TYPE_AS_PAYLOAD = "solr.TypeAsPayloadTokenFilterFactory"
    TYPE_AS_SYNONYM = "solr.TypeAsSynonymFilterFactory"

    # Payload filters
    NUMERIC_PAYLOAD = "solr.NumericPayloadTokenFilterFactory"
    TOKEN_OFFSET_PAYLOAD = "solr.TokenOffsetPayloadTokenFilterFactory"
    DELIMITED_PAYLOAD = "solr.DelimitedPayloadTokenFilterFactory"

    # Pattern filters
    PATTERN_REPLACE = "solr.PatternReplaceFilterFactory"
    PATTERN_CAPTURE_GROUP = "solr.PatternCaptureGroupFilterFactory"

    # Hyphenated words
    HYPHENATED_WORDS = "solr.HyphenatedWordsFilterFactory"

    # Capitalization
    CAPITALIZATION = "solr.CapitalizationFilterFactory"

    # Fingerprint
    FINGERPRINT = "solr.FingerprintFilterFactory"

    # Elision
    ELISION = "solr.ElisionFilterFactory"

    # Apostrophe
    APOSTROPHE = "solr.ApostropheFilterFactory"

    # Flatten graph (required after graph filters in index analyzer)
    FLATTEN_GRAPH = "solr.FlattenGraphFilterFactory"

    # Code point count
    CODE_POINT_COUNT = "solr.CodepointCountFilterFactory"

    # Concatenate graph
    CONCATENATE_GRAPH = "solr.ConcatenateGraphFilterFactory"

    # Limit token count
    LIMIT_TOKEN_COUNT = "solr.LimitTokenCountFilterFactory"
    LIMIT_TOKEN_OFFSET = "solr.LimitTokenOffsetFilterFactory"
    LIMIT_TOKEN_POSITION = "solr.LimitTokenPositionFilterFactory"

    # ICU-based filters
    ICU_NORMALIZER2 = "solr.ICUNormalizer2FilterFactory"
    ICU_TRANSFORM = "solr.ICUTransformFilterFactory"

    # Japanese-specific filters
    JAPANESE_BASE_FORM = "solr.JapaneseBaseFormFilterFactory"
    JAPANESE_PART_OF_SPEECH_STOP = "solr.JapanesePartOfSpeechStopFilterFactory"
    JAPANESE_KATAKANA_STEM = "solr.JapaneseKatakanaStemFilterFactory"
    JAPANESE_READING_FORM = "solr.JapaneseReadingFormFilterFactory"

    # Korean-specific filters
    KOREAN_PART_OF_SPEECH_STOP = "solr.KoreanPartOfSpeechStopFilterFactory"
    KOREAN_READING_FORM = "solr.KoreanReadingFormFilterFactory"

    # Compound word filters
    DICTIONARY_COMPOUND_WORD = "solr.DictionaryCompoundWordTokenFilterFactory"
    HYPHENATION_COMPOUND_WORD = "solr.HyphenationCompoundWordTokenFilterFactory"

    # Keyword repeat and marker
    KEYWORD_REPEAT = "solr.KeywordRepeatFilterFactory"
    KEYWORD_MARKER = "solr.KeywordMarkerFilterFactory"

    # Morfologik (lemmatization)
    MORFOLOGIK = "solr.MorfologikFilterFactory"

    # OpenNLP filters
    OPENNLP_POS = "solr.OpenNLPPOSFilterFactory"
    OPENNLP_CHUNKER = "solr.OpenNLPChunkerFilterFactory"
    OPENNLP_NER = "solr.OpenNLPNERFilterFactory"
    OPENNLP_LEMMATIZER = "solr.OpenNLPLemmatizerFilterFactory"

    # Reversed wildcard
    REVERSED_WILDCARD = "solr.ReversedWildcardFilterFactory"

    # Delimited term frequency
    DELIMITED_TERM_FREQUENCY = "solr.DelimitedTermFrequencyTokenFilterFactory"

    # Min hash
    MINHASH = "solr.MinHashFilterFactory"

    # Concatenate
    CONCATENATE = "solr.ConcatenateFilterFactory"

    # Drop if flagged
    DROP_IF_FLAGGED = "solr.DropIfFlaggedFilterFactory"

    # Fixed shingle
    FIXED_SHINGLE = "solr.FixedShingleFilterFactory"

    # Decimal digit
    DECIMAL_DIGIT = "solr.DecimalDigitFilterFactory"

    # CJK filters
    CJK_BIGRAM = "solr.CJKBigramFilterFactory"
    CJK_WIDTH = "solr.CJKWidthFilterFactory"

    def __str__(self) -> str:
        return self.value


class SolrCharFilterFactory(str, Enum):
    """Type-safe enum for Solr/Lucene char filter factory classes.

    Char filters process the raw character stream before tokenization, performing
    operations like HTML stripping or character mapping.
    Each enum member maps to a char filter factory class name using the short notation
    (e.g., `solr.HTMLStripCharFilterFactory`).

    Categories:
        - HTML/Markup: HTML_STRIP
        - Pattern-based: PATTERN_REPLACE
        - Mapping: MAPPING
        - ICU: ICU_NORMALIZER2

    Example:
        ```python
        from taiyo.schema.enums import SolrCharFilterFactory

        analyzer_config = {
            "charFilters": [
                {"class": SolrCharFilterFactory.HTML_STRIP},
                {"class": SolrCharFilterFactory.MAPPING, "mapping": "mapping-FoldToASCII.txt"}
            ],
            "tokenizer": {"class": "solr.StandardTokenizerFactory"}
        }
        ```

    Reference:
        https://solr.apache.org/guide/solr/latest/indexing-guide/charfilters.html
    """

    # HTML stripping
    HTML_STRIP = "solr.HTMLStripCharFilterFactory"

    # Pattern-based replacement
    PATTERN_REPLACE = "solr.PatternReplaceCharFilterFactory"

    # Character mapping
    MAPPING = "solr.MappingCharFilterFactory"

    # ICU normalization
    ICU_NORMALIZER2 = "solr.ICUNormalizer2CharFilterFactory"

    # Persian char filter
    PERSIAN = "solr.PersianCharFilterFactory"

    def __str__(self) -> str:
        return self.value
