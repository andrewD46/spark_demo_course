#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from typing import Any, Dict, Iterable, Optional, Union

maximum: Any
minimum: Any
sqrt: Any

class StatCounter:
    n: int
    mu: float
    m2: float
    maxValue: float
    minValue: float
    def __init__(self, values: Optional[Iterable[float]] = ...) -> None: ...
    def merge(self, value: float) -> StatCounter: ...
    def mergeStats(self, other: StatCounter) -> StatCounter: ...
    def copy(self) -> StatCounter: ...
    def count(self) -> int: ...
    def mean(self) -> float: ...
    def sum(self) -> float: ...
    def min(self) -> float: ...
    def max(self) -> float: ...
    def variance(self) -> float: ...
    def sampleVariance(self) -> float: ...
    def stdev(self) -> float: ...
    def sampleStdev(self) -> float: ...
    def asDict(self, sample: bool = ...) -> Dict[str, Union[float, int]]: ...
