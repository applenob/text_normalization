# Text Normalization for English

## 问题描述
所谓“文本正则”，即将手写形式的文本转换成语音形式的文本。

例子：

- 手写：`A baby giraffe is 6ft tall and weighs 150lb.`
- 语音：`A baby giraffe is six feet tall and weighs one hundred fifty pounds.`

## 调研
目前kernel上主要以收集大辞典的方法为主流。

基于RNN的方法在paper中提到说效果不佳。

token的所有类别：`['PLAIN', 'PUNCT', 'DATE', 'LETTERS', 'CARDINAL', 'VERBATIM', 'DECIMAL', 'MEASURE', 'MONEY', 'ORDINAL', 'TIME', 'ELECTRONIC', 'DIGIT', 'FRACTION', 'TELEPHONE', 'ADDRESS']`。
其中，`'PLAIN', 'PUNCT'`是输出和输入相同的类别。但训练数据中，只有`'PUNCT'`的输出和输入完全相同，`'PLAIN'`的输入和输出相同的个数是：7317175，总共个数是：7353693。比例是：0.995034059757458。这里后续需要继续调查。
其他所有的类别，输入和输出都不一样。

在训练集中，`'PLAIN', 'PUNCT'`所占的比例是0.931。

## 解决方法进化记录
### 2017-11-2

![]()

0.9937-198/489

使用kernel中提供的方法尝试了一下。大致上就是从训练语料中提取一个大辞典，这个词典包括所有词以及其映射。不同的方法引进了更多的额外训练语料。

### 2017-11-5

![]()

0.9164

用xgboost训练了一个二分类器，判别某个token是不是属于`'PLAIN', 'PUNCT'`。是则输入和输出相同，否则输出`""`。得到这个准确率。

### 2017-11-6


## 使用到的第三方包

`roman`， `num2words`， `inflect`
