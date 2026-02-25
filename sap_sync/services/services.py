from django.utils import timezone

from .connections import SAPConnection , Queries
from ..models import syncLogs , Products , Party

class ProductServices:
    
    def __init__(self):
        self.connection = SAPConnection()
        
    def syncProducts(self):
        products = []
        log = syncLogs.objects.create(
            sync_type = 'PRD',
            status = 'STR',
            triggered_by = 'Manual',
            started_at = timezone.now()
        )
        
        try:
            with self.connection as conn:
                # Assuming you are using the static method on SAPConnection now
                query = Queries.get_all_product()
                result = conn.execute_query(query) 
                
            for row in result:
                item_code = str(row.get('ItemCode' , ' ')).strip()
                if not item_code:
                    continue
                
                products.append(
                    Products(
                        item_code = item_code,
                        item_name = row.get('ItemName'),
                        category = row.get('Category'),
                        sal_factor2 = row.get('SalFactor2'),
                        u_tax_rate = row.get('U_Rev_tax_Rate') or row.get('U_Tax_Rate') or 0,
                        deleted = row.get('Deleted'),
                        u_variety = row.get('U_Variety'),
                        sal_pack_un = row.get('SalPackUn'),
                        u_brand = row.get('U_Brand'),
                        u_unit = row.get('U_Unit'),
                        u_sub_group = row.get('U_Sub_Group')
                    )
                )

            if products:
                Products.objects.bulk_create(
                        products,
                        batch_size=1000,
                        update_conflicts=True,
                        unique_fields=['item_code'], 
                        update_fields=['item_name', 'category', 'sal_factor2', 'u_tax_rate', 'deleted', 'u_variety', 'sal_pack_un', 'u_brand','u_unit', 'u_sub_group']
                    )
                   
            log.status = 'SCS'
            log.completed_at = timezone.now()
            log.records_procesed = len(products)
            log.save()
            
            return len(products)
                
        except Exception as e:
            # --- NEW FIX: Update the log to Failed before raising the exception ---
            log.status = 'FLD'
            log.completed_at = timezone.now()
            log.error_message = str(e)
            log.save()
            
            raise Exception(f"Service Error: {str(e)}")
    
    def syncProduct(self , itemCode):
        log = syncLogs.objects.create(
            sync_type = 'PRD',
            status = 'STR',
            triggered_by = 'Manual',
            started_at = timezone.now()
        )

        try:
            with self.connection as conn:
                query =  Queries.get_single_product(itemCode)
                result = conn.execute_query(query)
                
            if not result:
                raise Exception("No data returned")
            
            row = result[0]
            item_code = str(row.get('ItemCode' , ' ')).strip()
            if not item_code:
                raise Exception("No item Code (Unique Value) Found")
            
            product_obj , created = Products.objects.update_or_create(
                item_code=item_code,
                defaults={
                    'item_name': row.get('ItemName'),
                    'category': row.get('Category'),
                    'sal_factor2': row.get('SalFactor2'),
                    'u_tax_rate': row.get('U_Tax_Rate'),
                    'deleted': row.get('Deleted'),
                    'u_variety': row.get('U_Variety'),
                    'sal_pack_un': row.get('SalPackUn'),
                    'u_brand': row.get('U_Brand'),
                    'u_unit': row.get('U_Unit'),
                    'u_sub_group': row.get('U_Sub_Group')
                }
            )
            
            log.status = 'SCS'
            log.completed_at = timezone.now()
            log.records_procesed = 1
    
            
            return product_obj
        
        except Exception as e:
            
            log.status = 'FLD'
            log.error_message = str(e)
            log.save()
            
            raise Exception(f"Service Error: {str(e)}")
    
                
    
    
class PartyServices:
    
    def __init__(self):
        self.connection = SAPConnection()
    
    def syncParty(self,cardCode):
        if not cardCode:
            raise Exception("Please Provide Card Code")
        
        
        log = syncLogs.objects.create(
            sync_type = 'PRT',
            status = 'STR',
            triggered_by = 'Manual',
            started_at = timezone.now()
        )
        
        try:
            party = []
            with self.connection as conn:
                query = Queries.get_single_party(cardCode)
                result = conn.execute_query(query)

            if not result:
                raise Exception("No data returned")
            
            
            row = result[0]
            card_code = str(row.get('CardCode' , ' ')).strip()
            if not card_code:
                raise Exception("No card Code (Unique Value) Found")
            
            party_obj , created = Party.objects.update_or_create(
                card_code=card_code,
                defaults={
                    'card_name': row.get('CardName'),
                    'state' : row.get('State1'),
                    'u_main_group' : row.get('U_Main_Group'),
                    'country' : row.get('Country')
                }
            )
            log.status = 'SCS'
            log.completed_at = timezone.now()
            log.records_procesed = 1
            if created:
                log.records_created = 1
            else:
                log.records_updated = 1
            log.save()
            
            return party_obj
        
        except Exception as e:
            
            log.status = 'FLD'
            log.error_message = str(e)
            log.save()
            
            raise Exception(f"Service Error: {str(e)}")
    
                