

class OCRService(object):

    def check_available(self):
        return True

    def extract_text_from_image(self, data, languages=None):
        raise NotImplemented()


# class OfficeConverterService(object):
#
#     def check_available(self):
#         return True
#
#     def convert_to_pdf(self, file_path, file_name, mime_type):
#         pass
