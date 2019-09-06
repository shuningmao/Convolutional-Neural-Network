import logging
import re
import csv
import numpy as np
import lib.tools as tools
import json

class Cleaner(object):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    @staticmethod
    def count_lines(fname):
        i = -1
        with open(fname, 'r') as f:
            for i, l in enumerate(f):
                pass
        return i

    def log_file(self, num, fn):
        self.logger.info(' saved %s instances to %s', num, fn)


    def split(self, dst_inp, dst_out1, dst_out2, train=0.7, dev=0.15, test=0.15):
        srcs = tools.read_all_files(dst_inp)
        srcs_sorted = sorted(srcs)

        for i in range(3, len(srcs_sorted)):
            srcs_labeled = []
            tot_rows = 0
            for j in range(1, 4):
                src_fn = srcs_sorted[i-j]
                tot_rows += self.count_lines(dst_inp + src_fn)
                srcs_labeled.append(src_fn)

            train_num = np.int(np.ceil(train * tot_rows))
            dev_num = np.int(np.floor(dev * tot_rows))
            test_num = np.int(np.floor(test * tot_rows))

            train_fn = srcs_sorted[i].replace('.csv', '_train.csv')
            dev_fn = srcs_sorted[i].replace('.csv', '_dev.csv')
            test_fn = srcs_sorted[i].replace('.csv', '_test.csv')

            with open(dst_out1 + train_fn, 'w') as train_f, \
                    open(dst_out1 + dev_fn, 'w') as dev_f, \
                    open(dst_out2 + test_fn, 'w') as test_f:

                train_writer = csv.writer(train_f)
                dev_writer = csv.writer(dev_f)
                test_writer = csv.writer(test_f)

                header = ['GUID', 'Date', 'Content', 'Annotation', 'Ambiguous']
                train_writer.writerow(header)
                dev_writer.writerow(header)
                test_writer.writerow(header)

                rows = []
                for src_fn in srcs_labeled:
                    with open(dst_inp + src_fn, 'r') as src_f:
                        reader = csv.reader(src_f)
                        next(reader)
                        for row in reader:
                            row[2] = self._clean_txt(row[2])
                            rows.append(row)

                # shuffle the files so that the rows from the same file can be mixed into training, dev or test
                rows_shuffle = tools.shuffle_file(rows)
                m, num, writer = 0, train_num, train_writer
                for n in range(len(rows_shuffle)):
                    if m >= num:
                        if writer == train_writer:
                            self.log_file(train_num, train_fn)
                            m, num, writer = 0, dev_num, dev_writer
                        elif writer == dev_writer:
                            self.log_file(dev_num, dev_fn)
                            m, num, writer = 0, test_num, test_writer
                        else:
                            self.log_file(test_num, test_fn)
                            break
                    writer.writerow(rows_shuffle[n])
                    m += 1

    @staticmethod
    def json_re_file(base_file, dst_inp, dst_out, version):
        # srcs would be the FOMC meeting dates: e.g. 2015-06
        srcs = tools.read_all_files(dst_inp)
        srcs_sorted = sorted(srcs)
        srcs = srcs_sorted[3:]
        with open(base_file, 'r') as f1:
            base = json.load(f1)

        for src in srcs:
            base_temp = dict(base)
            for key, value in base_temp.items():
                if isinstance(value, str) and "<file>" in value:
                        base_temp[key] = value.replace("<file>", src[:-4])
                if isinstance(value, str) and "<version>" in value:
                        base_temp[key] = base_temp[key].replace("<version>", version)
            fn = src.replace(".csv", "_" + version + "_config.json")
            with open(dst_out + fn, 'w') as f:
                json.dump(base_temp, f)



    @staticmethod
    def _clean_txt(row):
        content = row.strip().lower()
        # remove links/emails
        content = re.sub(r'(\w+://[^\s]+)|([\w.-]+@[\w.-]+)', '', content)
        # remove extra whitespaces
        content = re.sub(r'\s+', ' ', content)
        # shrink ?!,...
        content = re.sub(r'\!{2,}', '!', content)
        content = re.sub(r'\?{2,}', '?', content)
        content = re.sub(r'[\!\?]{2,}', '!?', content)
        content = re.sub(r'\,{2,}', ',', content)
        content = re.sub(r'\.{2,}', '...', content)
        # space around @/#/numbers/dates/words/special chars
        content = re.sub(r'([@#]\w+|[\d.,/]*\d+|[a-z]+|\.{3}|\!\?'
                         r'|[\"\'~`!$%&*?.,,])', r' \g<1> ', content)
        # remove everything not character or numbers
        #content = re.sub('[^A-Za-z0-9]+', ' ', content)
        content = ''.join(e for e in content if e.isalnum() or e.isspace())
        # remove extra whitespaces again
        content = re.sub(r'\s+', ' ', content)
        return content
