"""
Payment Processing Service
Handles payment processing, earnings calculation, and payouts
"""

from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import logging
from yookassa import Configuration, Payment
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.transaction import Transaction
from app.models.master import Master
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure YooKassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


class PaymentService:
    """Service for handling all payment operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.commission_rate = settings.PLATFORM_COMMISSION_RATE
    
    def calculate_earnings(
        self,
        client_cost: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate earnings breakdown
        
        Args:
            client_cost: Total amount paid by client
            
        Returns:
            Dictionary with master_earnings, platform_commission, payment_gateway_fee
        """
        # Payment gateway fee (2%)
        gateway_fee = client_cost * Decimal("0.02")
        
        # Amount after gateway fee
        net_amount = client_cost - gateway_fee
        
        # Platform commission (25% of net amount)
        platform_commission = net_amount * Decimal(str(self.commission_rate))
        
        # Master earnings
        master_earnings = net_amount - platform_commission
        
        return {
            "client_cost": client_cost,
            "gateway_fee": gateway_fee,
            "platform_commission": platform_commission,
            "master_earnings": master_earnings
        }
    
    async def create_payment(
        self,
        job: Job,
        payment_method: str = "card",
        return_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create payment transaction via YooKassa
        
        Args:
            job: Job object with payment details
            payment_method: Payment method type
            return_url: URL to return after payment
            
        Returns:
            Payment confirmation data with payment URL
        """
        try:
            # Create payment object
            payment = Payment.create({
                "amount": {
                    "value": str(job.client_cost),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url or "https://example.com/payment/success"
                },
                "capture": True,
                "description": f"Оплата работ по заказу {job.id}",
                "metadata": {
                    "job_id": str(job.id),
                    "master_id": str(job.master_id)
                }
            })
            
            # Save transaction record
            transaction = Transaction(
                job_id=job.id,
                master_id=job.master_id,
                amount=job.client_cost,
                payment_method=payment_method,
                gateway_transaction_id=payment.id,
                status='pending'
            )
            
            self.db.add(transaction)
            await self.db.commit()
            
            logger.info(f"Payment created: {payment.id} for job {job.id}")
            
            return {
                "payment_id": payment.id,
                "status": payment.status,
                "confirmation_url": payment.confirmation.confirmation_url if payment.confirmation else None,
                "amount": payment.amount.value,
                "currency": payment.amount.currency
            }
            
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            raise
    
    async def process_cash_payment(
        self,
        job: Job,
        master: Master
    ) -> Dict[str, Any]:
        """
        Process cash payment manually confirmed by master
        
        Args:
            job: Job object
            master: Master who received cash
            
        Returns:
            Transaction confirmation data
        """
        try:
            # Create transaction record
            transaction = Transaction(
                job_id=job.id,
                master_id=master.id,
                amount=job.client_cost,
                payment_method='cash',
                status='success',
                gateway_transaction_id=f"CASH-{datetime.now().timestamp()}"
            )
            
            self.db.add(transaction)
            
            # Update job status
            job.status = 'paid'
            
            await self.db.commit()
            
            # Calculate and transfer earnings
            payout_result = await self.payout_to_master(
                master,
                job.master_earnings
            )
            
            logger.info(f"Cash payment processed for job {job.id}")
            
            return {
                "transaction_id": str(transaction.id),
                "amount": str(transaction.amount),
                "status": "success",
                "payout": payout_result
            }
            
        except Exception as e:
            logger.error(f"Error processing cash payment: {e}")
            raise
    
    async def verify_payment(
        self,
        payment_id: str
    ) -> bool:
        """
        Verify payment status with YooKassa
        
        Args:
            payment_id: YooKassa payment ID
            
        Returns:
            True if payment is successful
        """
        try:
            payment = Payment.find_one(payment_id)
            
            if payment.status == 'succeeded':
                # Update transaction status
                transaction = await self._get_transaction_by_gateway_id(payment_id)
                
                if transaction:
                    transaction.status = 'success'
                    await self.db.commit()
                    
                    logger.info(f"Payment verified: {payment_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return False
    
    async def payout_to_master(
        self,
        master: Master,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Transfer earnings to master's account
        
        Args:
            master: Master to receive payout
            amount: Amount to transfer
            
        Returns:
            Payout confirmation data
        """
        try:
            # TODO: Implement actual bank transfer via API
            # For MVP, we log the transaction
            
            logger.info(f"Payout to master {master.id}: {amount} RUB")
            
            # In production, integrate with:
            # - Bank API for direct transfers
            # - YooKassa Payouts API
            # - Other payment providers
            
            return {
                "master_id": str(master.id),
                "amount": str(amount),
                "status": "processed",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing payout: {e}")
            raise
    
    async def handle_payment_webhook(
        self,
        webhook_data: Dict[str, Any]
    ) -> bool:
        """
        Handle payment webhook from YooKassa
        
        Args:
            webhook_data: Webhook payload from YooKassa
            
        Returns:
            True if webhook processed successfully
        """
        try:
            event_type = webhook_data.get('event')
            payment_object = webhook_data.get('object')
            
            if event_type == 'payment.succeeded' and payment_object:
                payment_id = payment_object.get('id')
                metadata = payment_object.get('metadata', {})
                job_id = metadata.get('job_id')
                
                if job_id:
                    # Update job and transaction status
                    await self._complete_job_payment(job_id, payment_id)
                    
                    logger.info(f"Webhook processed: payment.succeeded for job {job_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return False
    
    async def _get_transaction_by_gateway_id(
        self,
        gateway_id: str
    ) -> Optional[Transaction]:
        """Get transaction by payment gateway ID"""
        from sqlalchemy import select
        
        query = select(Transaction).where(
            Transaction.gateway_transaction_id == gateway_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _complete_job_payment(
        self,
        job_id: str,
        payment_id: str
    ):
        """Complete job payment process"""
        from sqlalchemy import select
        
        # Get job
        query = select(Job).where(Job.id == job_id)
        result = await self.db.execute(query)
        job = result.scalar_one_or_none()
        
        if not job:
            return
        
        # Update job status
        job.status = 'paid'
        job.completed_at = datetime.now()
        
        # Update transaction
        transaction = await self._get_transaction_by_gateway_id(payment_id)
        if transaction:
            transaction.status = 'success'
        
        await self.db.commit()
        
        # Trigger payout to master
        master_query = select(Master).where(Master.id == job.master_id)
        master_result = await self.db.execute(master_query)
        master = master_result.scalar_one_or_none()
        
        if master:
            await self.payout_to_master(master, job.master_earnings)
    
    def generate_receipt(
        self,
        job: Job,
        transaction: Transaction
    ) -> Dict[str, Any]:
        """
        Generate electronic receipt
        
        Args:
            job: Job object
            transaction: Transaction object
            
        Returns:
            Receipt data
        """
        return {
            "receipt_id": f"REC-{transaction.id}",
            "job_id": str(job.id),
            "date": datetime.now().isoformat(),
            "amount": str(transaction.amount),
            "payment_method": transaction.payment_method,
            "description": f"Работы по заказу {job.id}",
            "category": job.category,
            "master_info": {
                "id": str(job.master_id)
            }
        }
