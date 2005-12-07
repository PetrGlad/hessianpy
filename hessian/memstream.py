#
# Copyright 2005 Petr Gladkikh (batyi at mail ru)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

class MemStream:
    "Emulates file, reads/writes data from/to given string"
    data = ""
    pos = 0

    def read(self, count):
        assert count >= 0
        result = self.data[self.pos : self.pos + count]
        self.pos += count
        return result
    
    def seek(self, pos):
        self.pos = pos

    def write(self, data):        
        self.data = self.data[0 : self.pos] + data
        self.pos += len(data)


def testMemStream():
    s = MemStream()
    assert s.read(1) == ""
    s.write("")
    assert s.read(1) == ""    
    s.seek(0)
    assert s.read(1) == ""
    s.write("q")
    assert s.read(1) == ""
    s.seek(0)
    assert s.read(1) == "q"
    s.seek(0)
    assert s.read(2) == "q"
    s.seek(0)
    assert s.read(0) == ""
    s.write("byte")
    s.seek(0)
    assert s.read(10) == "byte"
    s.seek(2)
    assert s.read(10) == "te"
    s.seek(2)
    s.write("n")
    s.seek(0)
    assert s.read(10) == "byn"
    s.seek(0)
    s.write("l")
    s.write("oaf")
    s.seek(0)    
    assert s.read(2) == "lo"
    assert s.read(2) == "af"


if __name__ == "__main__":
    testMemStream()
