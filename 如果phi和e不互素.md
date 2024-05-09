# 如果phi和e不互素

如果p，q已知，且q-1或p-1与e的公因数比较大，可以尝试把p和q中和e不互素的q或者p去掉

# 知道 n,c,m求e的函数

```python
e = discrete_log(n,c,m)
#参数分别为n，c，m且n必须是两个质数相乘
```

# 将16进制转化成10进制输出

~~~python
c = [eval('0x'+ x) for x in open('Problem.txt', 'r').readlines()]
m1 = c[0]
for i in range(1,len(c)):
    temp = hex(m1 ^ c[i])[2:]
    for i in range(0,len(temp),2):
        pd = chr(eval('0x'+temp[i:i+2]))
        print(pd,end='')
    print()
~~~

# sympy库中的nthroot_mod()函数来求m

~~~ 
m=nthroot_mod(c,e,p)
~~~



