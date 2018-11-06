# clasp
A scheme-like interpreter written in Python. 

Inspired by this good article by Norvig: http://norvig.com/lispy.html

```scheme
; Clasp is a weird scheme by Claudio. 
; These are some basic functions and sanity checks.

(def - (=> (a b) (+ a (* -1 b))))

(def assert (=> (test)
    (if (not test) (raise "assert failed"))))

(def assert-equal (=> (a b)
    (assert (eq? a b))))

(def squared (=> (x) (* x x)))

(def sum (=> l (reduce l +)))

(def mul (=> l (reduce l *)))

(def range (=> (start end)
    (if (eq? start end)
        (list)
        (cons start (range (+ start 1) end)))))

(def for (=> (start end f)
    (let (i 0)
        (while (< i end) (begin
            (f i)
            (set! i (+ i 1)))))))

(def fibonacci (=> n
    (if (or (eq? n 1) (eq? n 2)) 1
        (+ (fibonacci (- n 1)) (fibonacci (- n 2))))))

(assert-equal (- 10 4) 6)
(assert-equal (+ 1.1 1) 2.1)
(assert-equal (fibonacci 7) 13)
(assert-equal (squared 10) 100)
(assert-equal (len (range 0 10)) 10)
(assert-equal (sum (range 0 10)) 45)
(assert-equal (str "hello" " " "world") "hello world")
(assert-equal (let (x 1 y 2) (+ x y)) 3)
(assert-equal
    (let (i 0) (begin
        (set! i (+ i 1))
        i))

;;; Python eval

(assert-equal (py "1+1") 2)
(assert-equal (sum (py "[i for i in range(10)]")) (sum (range 0 11)))
```
