# 1. Two Sum

**Difficulty:** Easy

## Problem

Given an array `nums` and a `target`, return the **indices of two numbers that add up to the target**.

Each input has exactly one solution, and you cannot use the same element twice.

### Example

```text
nums = [2, 7, 11, 15]
target = 9

Output: [0, 1]
```

Because:

```text
2 + 7 = 9
```

## Solution

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        num_dict = {}

        for i, num in enumerate(nums):
            complement = target - num

            if complement in num_dict:
                return [num_dict[complement], i]

            num_dict[num] = i

        return []
```

## In simple terms:

We use `num_dict` to **remember the numbers we've already seen and their indexes**.

For each number, we calculate:

```python
complement = target - num
```

This tells us what number we need to reach the target.

For example:

```text
target = 9
num = 7

9 - 7 = 2
```

We then check if `2` is already in our dictionary. If it is, we have found the two numbers and return their indexes.

If it isn't, we store the current number and its index:

```python
num_dict[num] = i
```

### Key note

> **Find what you need, check if you've already seen it, and if not, remember the current number.**



#### #ph1n3y
