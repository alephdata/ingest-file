# Usage

Ingestors operate on files and folders. And while some files represent a single
document, some file types include multiple documents, some of which of
different type.

A good example is an email file type. While the document is composed of a
subject and a body with address fields, it can also have attachments.

Because of this, an ingestor is composed of two parts: one is the file type
specific part to extract the information, the other part is designed to
discover and spawn additional ingestors based on the file type of contained
documents.

## Children

Any newly spawned ingestor will keep a reference to its parent by being
provided a file  value besides other context information.

An example of running an ingestor on an archive with multiple files looks like:

```
(checksum=24ds23, filename=data.txt)---
                                       |--(checksum=8ufd221, filename='1.eml')
(checksum=45k3c2, filename=pic.jpg)----                    |
                                                           |
                                          (checksum=7sydak3, filename='emails')
                                                           |
                                                           |
                                          (checksum=8734s1k, filename='my.zip')
```

Running an ingestor on the `archive.zip` will generate an checksum of the file
to be used as an identifier. Next it will extract the files and try to spawn a
new ingestor with the reference to the `archive.zip` instance. And so on with
every next file.

The ingestor offers support for iterating on all the children it discovered.

An example would be:

```python
for child in ingestor.children:
  if child.success:
    print child.checksum, child.filename, child.parent.checksum
```

## States

An ingestor can be in only one of the following states:
* *new*, indicates the ingestor was initiated, but no processing was done yet
* *started*, indicates the ingestor is still working
* *finished*, indicates the ingestor is done working

## Statuses

An ingestor can be in only one of the statuses:
* *success*, indicates the ingestor finished processing the file successfully
* *failure*, indicates the ingestor finished processing the file with an error
* *stopped*, indicates the ingestor was stopped externally or internally
  (system errors, OS limitations, etc.)

Along with the statuses, an ingestor having spawned children, provides
information the number of children and their status.

## Timing

An ingestor provides the timestamp it started and ended its execution.

## Events

An ingestor provides callbacks in the form of:
* `before()`, to be called before the file processing is started. This callback
  is provided with the context of the file to be processed (checksum information,
  filename, time it started, status etc.)
* `before_child()`, to be called by a spawned child ingestor with the same
  context it would call its own `before()` callback.
* `after()`, to be called after the file processing is done. This callback is
  provided with the context of the processed file and the results (spawned
  children, time it ended, status, etc.)
* `after_child()`, to be called by a spawned child ingestor with the same
  context it would call its own `after()` callback.

Any of these callbacks can be overwritten to store the context in a persistent
way or be passed on towards additional processing.

## Results

An ingestor does not provide a strict format of the processing results, still,
its interface provides access to the following extracted data:

* mime type
* file name
* file size
* checksum
* document title (if any)
* document authors (if any)
* text
* page/order (if child)
