import smartpy as sp

class LedgerKey:
    def get_type():
        return sp.TRecord(holder = sp.TAddress, token_id = sp.TNat).layout(("holder", "token_id"))

    def make(owner, token_id):
        return sp.set_type_expr(sp.record(owner = owner, token_id = token_id), LedgerKey.get_type())

class TokenMetadataValue:
    def get_type():
        return sp.TRecord(
            token_id = sp.TNat,
            token_info = sp.TMap(sp.TString, sp.TBytes)
        ).layout(( "token_id", "token_info"))

class Token_id_set:
    def update(total_supply):
        return total_supply

class ZooNFT_FA2(sp.Contract):
    def __init__(self, metadata, admin):
        self.init(
            # 账本 ，big_map类似java中的map,键值对
            ledger = sp.big_map(tkey = LedgerKey.get_type() ,tvalue = sp.TNat),
            # token详细数据
            token_metadata = sp.big_map(tkey = sp.TNat, tvalue = TokenMetadataValue.get_type()),
            # 白名单
            initial_hodlers = sp.big_map(tkey = sp.TAddress, tvalue = sp.TNat),
            # 铸造费用
            mint_fee = sp.TNat,
            # 所有的tokens_id
            all_tokens = sp.set(t = sp.TNat),
            # 元数据,元数据是用 metadata_of_url 实用程序函数创建的,存储于ipfs
            metadata = metadata,
        )

    @sp.entry_point
    def update_mint_fee(self, params):
        sp.verify( ~self.is_paused() , "Contract is paused")
        sp.verify(sp.sender == self.data.administrator, "Only administrator can update mint fee")
        sp.set_type(params.fee, sp.TNat)
        sp.verify(params.fee > 0,"Mint fee must be positive")
        self.mint_fee = params.fee

    @sp.entry_point
    def update_total_supply(self, params):
        sp.verify( ~self.is_paused() , "contract is paused")
        # 设置只有管理员可以更新nft个数
        sp.verify(sp.sender == self.data.administrator, "Only administrator can update total supply")
        sp.set_type(params.total_supply, sp.set(sp.TNat))
        # 更新总的nft个数
        self.data.all_tokens = Token_id_set.update(params.total_supply)
        
    @sp.entry_point
    def mint(self, params):
        sp.verify( ~self.is_paused() , "Contract is paused")
        # 调用者是否在白名单中
        sp.verify(self.data.initial_hodlers.contains(sp.sender), "Address is not in the initial hodlers list")
        token_id = sp.len(self.data.all_tokens)
        # 验证token_id是否已经铸造
        sp.verify(~ self.data.all_tokens.contains(token_id), "Can't mint same token twice")
        # 铸造token_id
        user = LedgerKey.make(sp.sender, token_id)
        self.data.ledger[user] = 1
        # Record记录类似C的struct(结构体)
        self.data.token_metadata[token_id] = sp.record(token_id = token_id, token_info = params.metadata)
        # 更新token_id数据
        self.data.all_tokens.add(token_id)

    @sp.add_test(name = "ZooNFT")
    def test():
        scenario = sp.test_scenario()
        scenario.h1 = ("ZooNFT")
        admin = sp.test_account("admin")
        scenario.h2("Cryptobot Contract")
        z1 = ZooNFT_FA2(
            metadata = sp.metadata_of_url("ipfs://xxx"),
            admin = admin
        )
        scenario += z1