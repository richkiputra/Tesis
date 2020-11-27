from Savoir import Savoir
import time as t
import threading
from recordCPU import RecordCPU


class Multichain:
    def __init__(self, rpcuser, rpcpassword, rpchost, rpcport, chainname):
        self.rpcuser = rpcuser
        self.rpcpassword = rpcpassword
        self.rpchost = rpchost
        self.rpcport = rpcport
        self.chainname = chainnameH
        self.initApi()
        self.CPU = RecordCPU()

    def initApi(self):
        self.api = Savoir(self.rpcuser, self.rpcpassword, self.rpchost, self.rpcport, self.chainname)

    # param stream (nama stream), num (jumlah data yg ingin di return)
    def listStreamItems(self, stream, num=0, isSearch = False):

        start = t.time()

        if num == 0:
            items = self.api.liststreamitems(stream)
        else:
            items = self.api.liststreamitems(stream)
            items = items[-num:]

        if(isSearch):
            end = t.time()
            t.sleep(3)
            self.CPU.is_mining = False
            self.CPU.record_cpu = False

            self.CPU.search_results = items
            time = end - start
            self.CPU.search_time.append(round(time,2))
            print('Waktu pencarian' + str(round(time,2)))
            print(self.CPU.search_results)

        else:
            return items

    def searchItem(self, stream, num=0):
        def record():
            return self.CPU.recordCpuUsage('search')

        def search():
            return self.listStreamItems(stream, num, True)

        self.CPU.is_mining = True
        self.CPU.record_cpu = True

        threading.Thread(target = record).start()
        t.sleep(3)
        threading.Thread(target = search).start()


    # belum selesai (untuk melihat detail item)
    def getStreamItems(self, stream, num):
        item = self.listStreamItems(stream, num)

        data = self.api.getstreamitem(stream)
        return data

    # mendapatkan info miner
    def getMiner(self, txid):
        data = self.api.getwallettransaction(txid)
        block = self.api.getblock(data['blockhash'])

        return block['miner']

    def getStreamInfo(self, stream):
        '''

        :param stream:
        :return:
        '''
        return self.api.getstreaminfo(stream)

    # param opt1 (print data), opt (print confirmations)
    def printData(self, items, data = False, confirm = False, txid = False, all = True):
        '''

        :param items:
        :param opt1:
        :param opt2:
        :return:
        '''
        total_item = len(items)
        for x in range(total_item):
            if data :
                print(x, bytes.fromhex(items[x]['data']).decode('utf-8'))
                all = False
            if confirm :
                print(items[x]['confirmations'], '\n')
                all = False
            if txid:
                print(items[x]['txid'], '\n')
                all = False
            if all :
                print(items[x], '\n')

    def publishStream(self, stream, key, data):

        def isMining():
            return self.isMined(stream, data)

        def record():
            return self.CPU.recordCpuUsage('publish')

        self.CPU.is_mining = True
        self.CPU.record_cpu = True

        threading.Thread(target = record).start()
        t.sleep(3)

        self.api.publish(stream, key, data)

        threading.Thread(target = isMining).start()

        proses = ''

        while True:
            if self.CPU.is_mining == False:
                proses = 'done'
                break

        return proses

    def isMined(self, stream, data):
        '''

        :param stream:
        :param data:
        :return:
        '''

        global items

        # mendapatkan item terakhir (terbaru) dalam streams
        items = self.listStreamItems(stream, 1)

        # mengecek apakah item terakhir (terbaru) sama dengan data inputan terakhir
        while (items[0]['data'] != data):
            items = self.listStreamItems(stream, 1)

        # waktu awal item terakhir (terbaru) masuk ke dalam stream
        start = t.time()

        print('\nStream last item data : ' + str(items[0]['data']))
        print('Stream last item confirmations : ' + str(items[0]['confirmations']))

        # mengecek item terakhir (terbaru) apakah sudah di mining
        while (items[0]['confirmations'] == 0):
            items = self.listStreamItems(stream, 1)

        self.CPU.list_miner.append(self.getMiner(items[0]['txid']))
        # waktu saat item terakhir (terbaru) sudah di mining
        end = t.time()

        t.sleep(5)

        self.CPU.record_cpu = False
        self.CPU.is_mining = False

        # mendapatkan durasi proses mining
        mining_time = end - start
        self.CPU.publish_time.append(round(mining_time,2))

        print('\nStream last item data : ' + str(items[0]['data']))
        print('Stream last item confirmations : ' + str(items[0]['confirmations']))
        print('Waktu mining = ' + str(round(mining_time,2)))

# if __name__ == '__main__':
#     Chain1 = Multichain('multichainrpc', 'A4VZcuwWrn36bGCZLrJ5dgg1QUw6CTPPq8fu5jZfQPNc', 'localhost', '7190', 'dyr')
#
#     items = Chain1.listStreamItems('stream1', 10)
#     Chain1.printData(items, True)
#     print('\n')
#     for i in range(len(items)):
#         miner = Chain1.getMiner(items[i]['txid'])
#         print(i, miner)
#
#     miner = Chain1.getMiner(items[1]['txid'])
#     print(miner)
#
#     miner = Chain1.getMiner(items[2]['txid'])
#     print(miner)
#
#     miner = Chain1.getMiner(items[3]['txid'])
#     print(miner)