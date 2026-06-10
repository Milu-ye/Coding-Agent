import collections
from typing import List
import heapq

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        t = collections.defaultdict()
        for num in nums:
            t[num] += 1
        q =  []
        for key, value in t.items():
            heapq.heappush(q, (-value, key))
        res = []
        for _ in range(k):
            res.append(heapq.heappop(q)[1])
        return res
