# 按类别处理

## PLAIN
- 收集一个dict，先过这个dict，有命中则替换。
- 无命中则直接将输入输出。

## PUNCT
- 因为训练集中所有的PUNCT都是自己本身，所以直接将输入输出。

## DATE
### 样例

- `22 September 2015` -> `the twenty second of september twenty fifteen`
- `2006` -> `two thousand six`
- `April 10, 2013` -> `april tenth twenty thirteen`
- `11/17/09` -> `november seventeenth o nine`
- `2007-11-24` -> `the twenty fourth of november two thousand seven`
- `25-08-2015` -> `the twenty fifth of august twenty fifteen`
- `14 April` -> `the fourteenth of april`
- `June 2004` -> `june two thousand four`