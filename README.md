The gehpi rendering aspect of this project has been split off to: https://github.com/thisismattmiller/catalog-network-java check that repo for update catalog-network.jar


catalog-network
===============

Turn MARC records into a subject heading network

More development and documentation is needed. But the basic order to run things would be

marc2gexf/generate_gexf.py

java -jar render/dist/catalog-network.jar (need to pass files, and the render options are hard coded, TODO!)


interface/process.py

interface/build_index_documents.py

interface/build_index.py



---

License
====
The MIT License (MIT)

Copyright (c) 2014 Matt Miller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

---
* This project utilizes libraries which may or may not have additional individual licenses
