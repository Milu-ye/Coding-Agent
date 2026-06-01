import heapq
from typing import List


class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        if len(nums) == 0:
            return 1
        t = nums.copy()
        heapq.heapify(t)
        q = heapq.heappop(t)
        while len(t) != 0 and q <=0:
            q = heapq.heappop(t)
        if len(t) == 0 and q < 0:
            return 1
        if  q > 1:
            return 1
        pre = q + 1
        while len(t) != 0:
            cur = heapq.heappop(t)
            if pre > cur:
                return pre
            pre = cur + 1
        return pre