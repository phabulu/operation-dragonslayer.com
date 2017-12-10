import sys
from urllib import urlopen
import json
from util.slugify import slugify
from stats.calc import update_obj_by_rules

RULES = {

    'min': ['id'],
    'max': ['id', 'size', 'weight', 'difficulty', 'fee_per_kb_usd'],
    'sum': [
        'transaction_count',
        'witness_count',
        'input_count', 
        'output_count',
        'input_total_usd',
        'output_total_usd',
        'fee_total_usd',
        'cdd_total',
        'generation_usd',
        'reward_usd',
    ],

}

class BlockchairBitcoin(object):
    URL = "https://api.blockchair.com/bitcoin/blocks"
    
    def update(self, cls):
        data = json.loads(urlopen(self.URL).read())

        date = data["data"][0]["date"]

        obj = cls.get_by_id("bitcoin|%s" % date)
        if not obj:
            obj = cls(id="bitcoin|%s" % date)
        
        count = 0
        for block in data["data"]:
            if getattr(obj, "last_block", None):
                if block["id"] <= obj.last_block:
                    continue
            
            self.update_obj(obj, block)
            count += 1

        obj.put()
        return {"date": date, "count": count}

    def update_obj(self, obj, block):
        obj.date = block.get("date", "none")
        obj.block_count = getattr(obj, "block_count", 0) + 1
        miner = slugify(block.get("guessed_miner", "none"))
        setattr(obj, "miner_%s" % miner, getattr(obj, "miner_%s" % miner, 0) + 1)
        return update_obj_by_rules(obj, block, RULES)

    