import smartpy as sp

FA2 = sp.import_script_from_url("https://smartpy.io/templates/FA2.py")

class CryptoZoo(FA2.FA2):
    def __init__(self, config, metadata, admin):
        # 清单列表
        list_of_views = [
            self.get_balance
            , self.token_metadata
            , self.does_token_exist
            , self.count_tokens
            , self.all_tokens
            , self.is_operator
        ]
        # 元数据
        metadata_base = {
          "name": "3D CryptoZoo"
          , "version": "1.0"
          , "description" :"Users created NFT 3D CryptoZoo."
          , "interfaces": ["TZIP-12", "TZIP-16", "TZIP-21"]
          , "authors": [
              "Ekko"
          ]
          , "source": {
              "tools": ["SmartPy"]
              , "location": "https://smartpy.io/templates/FA2.py"
          },
          "date": "2022-05-08",
          "tags": ["3D", "CryptoZoo", "Collectables", "NFT"],
          "language": "en",
          "views": list_of_views
        }
        self.init_metadata("metadata_base", metadata_base)
        FA2.FA2_core.__init__(self, config, metadata,
            paused = False, administrator = admin,
            # 白名单
            initial_hodlers = sp.big_map(tkey = sp.TAddress, tvalue = sp.TNat))

    @sp.entry_point
    def transfer(self, params):
        # 验证合约是否运行
        sp.verify( ~self.is_paused() , "CONTRACT IS PAUSED")
        # 设置交易类型，批量交易
        sp.set_type(params, self.batch_transfer.get_type())
        sp.for transfer in params:
          current_from = transfer.from_
          sp.for tx in transfer.txs:
                if self.config.single_asset:
                    sp.verify(tx.token_id == 0, "single-asset: token-id <> 0")
                # 验证转账者是否是调用者
                sp.verify(current_from == sp.sender, message = self.error_message.not_owner())
                # 验证token是否存在
                sp.verify(self.data.tokens.contains(tx.token_id),
                          message = self.error_message.token_undefined())
                
                sp.if (tx.amount > 0):
                    from_user = self.ledger_key.make(current_from, tx.token_id)
                    sp.verify(
                        # 验证用户在当前合约的余额是否大于等于交易余额
                        (self.data.ledger[from_user].balance >= tx.amount),
                        message = self.error_message.insufficient_balance())
                    to_user = self.ledger_key.make(tx.to_, （tx.token_id，tx.amount*0.9))
                    to_self = self.ledger_key.make(sp.self_address, （tx.token_id，tx.amount*0.1))
                    # 更新用户余额
                    self.data.ledger[from_user].balance = sp.as_nat(
                        self.data.ledger[from_user].balance - tx.amount)
                    sp.if self.data.ledger.contains(to_user):
                        self.data.ledger[to_user].balance += tx.amount
                    sp.else:
                         self.data.ledger[to_user] = FA2.Ledger_value.make(tx.amount)
                sp.else:
                    pass
                
                # Remove bot from sale if true
                user = self.ledger_key.make(current_from, tx.token_id)
                
                #Make sure it's a valid user 
                sp.if self.data.ledger.contains(user):
                    sp.if self.data.offer.contains(tx.token_id):
                        # Remove NFT token id from offers list
                        del self.data.offer[tx.token_id]
