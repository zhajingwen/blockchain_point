import hashlib
import json
import time
from typing import List, Dict, Any
from copy import deepcopy


class Transaction:
    """交易类"""
    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
    
    def __repr__(self):
        return f"Transaction({self.sender} -> {self.recipient}: {self.amount})"


class Block:
    """区块类"""
    def __init__(self, index: int, transactions: List[Transaction], 
                 previous_hash: str, timestamp: float = None):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = 0
        self.hash = None
    
    def calculate_hash(self) -> str:
        """计算区块哈希"""
        block_data = {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int):
        """工作量证明挖矿"""
        target = '0' * difficulty
        print(f"开始挖矿区块 #{self.index}，难度: {difficulty}")
        start_time = time.time()
        
        while True:
            self.hash = self.calculate_hash()
            if self.hash[:difficulty] == target:
                elapsed = time.time() - start_time
                print(f"✓ 挖矿成功! 耗时: {elapsed:.2f}秒, Nonce: {self.nonce}")
                print(f"  区块哈希: {self.hash}")
                break
            self.nonce += 1
            
            # 每10000次尝试显示进度
            if self.nonce % 10000 == 0:
                print(f"  尝试次数: {self.nonce}...")
    
    def to_dict(self) -> Dict:
        return {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    def __repr__(self):
        return f"Block(#{self.index}, {len(self.transactions)} txs, hash={self.hash[:10]}...)"


class Blockchain:
    """区块链类"""
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = 10.0
        
        # 创建创世区块
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """创建创世区块"""
        print("创建创世区块...")
        genesis_block = Block(0, [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        print()
    
    def get_latest_block(self) -> Block:
        """获取最新区块"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction):
        """添加交易到待处理池"""
        self.pending_transactions.append(transaction)
        print(f"添加交易: {transaction}")
    
    def mine_pending_transactions(self, miner_address: str):
        """挖矿:将待处理交易打包进新区块"""
        if not self.pending_transactions:
            print("没有待处理的交易")
            return False
        
        print(f"\n{'='*60}")
        print(f"开始打包 {len(self.pending_transactions)} 笔交易")
        print(f"{'='*60}")
        
        # 创建新区块
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.get_latest_block().hash
        )
        
        # 工作量证明挖矿
        new_block.mine_block(self.difficulty)
        
        # 添加到区块链
        self.chain.append(new_block)
        
        # 清空待处理交易,添加挖矿奖励交易
        self.pending_transactions = [
            Transaction("系统", miner_address, self.mining_reward)
        ]
        
        print(f"✓ 区块 #{new_block.index} 已添加到区块链")
        print(f"  矿工 {miner_address} 获得 {self.mining_reward} 奖励\n")
        return True
    
    def get_balance(self, address: str) -> float:
        """获取地址余额"""
        balance = 0.0
        
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.recipient == address:
                    balance += tx.amount
        
        # 计算待处理交易
        for tx in self.pending_transactions:
            if tx.sender == address:
                balance -= tx.amount
            if tx.recipient == address:
                balance += tx.amount
        
        return balance
    
    def is_chain_valid(self) -> bool:
        """验证区块链完整性"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # 验证当前区块哈希
            if current.hash != current.calculate_hash():
                print(f"✗ 区块 #{i} 哈希不匹配")
                return False
            
            # 验证链接
            if current.previous_hash != previous.hash:
                print(f"✗ 区块 #{i} 链接断裂")
                return False
            
            # 验证工作量证明
            if not current.hash.startswith('0' * self.difficulty):
                print(f"✗ 区块 #{i} 工作量证明无效")
                return False
        
        return True
    
    def display_chain(self):
        """显示区块链"""
        print(f"\n{'='*60}")
        print(f"区块链信息 (共 {len(self.chain)} 个区块)")
        print(f"{'='*60}")
        
        for block in self.chain:
            print(f"\n区块 #{block.index}")
            print(f"  时间戳: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))}")
            print(f"  前区块哈希: {block.previous_hash[:20]}...")
            print(f"  当前哈希: {block.hash[:20]}...")
            print(f"  Nonce: {block.nonce}")
            print(f"  交易数量: {len(block.transactions)}")
            
            for tx in block.transactions:
                print(f"    - {tx.sender} -> {tx.recipient}: {tx.amount}")
    
    def sync_from_chain(self, external_chain: List[Dict]):
        """从外部链同步区块"""
        print(f"\n{'='*60}")
        print("开始节点同步...")
        print(f"{'='*60}")
        
        # 重建区块链
        new_chain = []
        for block_data in external_chain:
            # 重建交易
            transactions = [
                Transaction(tx['sender'], tx['recipient'], tx['amount'])
                for tx in block_data['transactions']
            ]
            
            # 重建区块
            block = Block(
                block_data['index'],
                transactions,
                block_data['previous_hash'],
                block_data['timestamp']
            )
            block.nonce = block_data['nonce']
            block.hash = block_data['hash']
            
            new_chain.append(block)
        
        # 验证新链
        temp_blockchain = Blockchain(self.difficulty)
        temp_blockchain.chain = new_chain
        
        if temp_blockchain.is_chain_valid() and len(new_chain) > len(self.chain):
            print("✓ 外部链有效且更长,替换本地链")
            self.chain = new_chain
            return True
        else:
            print("✗ 外部链无效或不够长,保持本地链")
            return False
    
    def export_chain(self) -> List[Dict]:
        """导出区块链数据"""
        return [block.to_dict() for block in self.chain]


# ============= 演示程序 =============
if __name__ == "__main__":
    print("=" * 60)
    print("区块链实践演示")
    print("=" * 60)
    
    # 1. 创建区块链(难度设为4)
    blockchain = Blockchain(difficulty=4)
    
    # 2. 添加交易
    print("\n【步骤1: 添加交易到交易池】")
    blockchain.add_transaction(Transaction("Alice", "Bob", 50))
    blockchain.add_transaction(Transaction("Bob", "Charlie", 25))
    blockchain.add_transaction(Transaction("Charlie", "Alice", 10))
    
    # 3. 挖矿打包交易
    print("\n【步骤2: 矿工挖矿打包交易】")
    blockchain.mine_pending_transactions("Miner1")
    
    # 4. 添加更多交易
    print("\n【步骤3: 添加新的交易】")
    blockchain.add_transaction(Transaction("Alice", "Charlie", 15))
    blockchain.add_transaction(Transaction("Bob", "Alice", 30))
    
    # 5. 再次挖矿
    print("\n【步骤4: 再次挖矿】")
    blockchain.mine_pending_transactions("Miner2")
    
    # 6. 显示区块链
    blockchain.display_chain()
    
    # 7. 查询余额
    print(f"\n{'='*60}")
    print("账户余额查询")
    print(f"{'='*60}")
    for address in ["Alice", "Bob", "Charlie", "Miner1", "Miner2"]:
        balance = blockchain.get_balance(address)
        print(f"{address:15} 余额: {balance}")
    
    # 8. 验证区块链
    print(f"\n{'='*60}")
    print("区块链验证")
    print(f"{'='*60}")
    is_valid = blockchain.is_chain_valid()
    print(f"区块链是否有效: {'✓ 是' if is_valid else '✗ 否'}")
    
    # 9. 模拟节点同步
    print(f"\n{'='*60}")
    print("【步骤5: 模拟节点同步】")
    print(f"{'='*60}")
    
    # 创建第二个节点
    node2 = Blockchain(difficulty=4)
    print(f"节点2当前区块数: {len(node2.chain)}")
    
    # 从节点1同步数据
    exported_chain = blockchain.export_chain()
    node2.sync_from_chain(exported_chain)
    print(f"节点2同步后区块数: {len(node2.chain)}")
    
    print("\n" + "="*60)
    print("演示完成!")
    print("="*60)