"""
初始化数据库和示例数据
运行方式: python -m app.init_db
"""
from datetime import datetime, timedelta
from app.database import Base, engine, SessionLocal
from app.models import (
    User, Part, Donation, DonationHistory, Bike, Pickup,
    Refurbishment, PartUsage, Recipient, Match
)
from app.auth import hash_password


def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Checking initial data...")

        if not db.query(User).filter(User.username == "admin").first():
            print("Creating default users...")
            users = [
                User(username="admin", email="admin@revivebike.org",
                     password_hash=hash_password("123456"),
                     full_name="系统管理员", phone="13800000000", role="admin"),
                User(username="volunteer1", email="volunteer1@revivebike.org",
                     password_hash=hash_password("123456"),
                     full_name="张志愿", phone="13800000001", role="volunteer"),
                User(username="volunteer2", email="volunteer2@revivebike.org",
                     password_hash=hash_password("123456"),
                     full_name="李爱心", phone="13800000002", role="volunteer"),
                User(username="donor1", email="donor1@example.com",
                     password_hash=hash_password("123456"),
                     full_name="王先生", phone="13900000001", role="donor"),
                User(username="donor2", email="donor2@example.com",
                     password_hash=hash_password("123456"),
                     full_name="刘女士", phone="13900000002", role="donor"),
                User(username="donor3", email="donor3@example.com",
                     password_hash=hash_password("123456"),
                     full_name="陈先生", phone="13900000003", role="donor"),
            ]
            for user in users:
                db.add(user)
            db.commit()
            print(f"Created {len(users)} users.")

        if not db.query(Part).first():
            print("Creating default parts...")
            parts = [
                Part(name="内胎", category="轮胎", sku="P-TYRE-001", stock_quantity=50, unit="条", description="26寸标准内胎"),
                Part(name="外胎", category="轮胎", sku="P-TYRE-002", stock_quantity=30, unit="条", description="26寸耐磨外胎"),
                Part(name="刹车皮", category="刹车系统", sku="P-BRAKE-001", stock_quantity=100, unit="对", description="V刹刹车皮"),
                Part(name="刹车线", category="刹车系统", sku="P-BRAKE-002", stock_quantity=80, unit="根", description="不锈钢刹车线"),
                Part(name="链条", category="传动系统", sku="P-DRIVE-001", stock_quantity=40, unit="条", description="8速链条"),
                Part(name="飞轮", category="传动系统", sku="P-DRIVE-002", stock_quantity=25, unit="个", description="8速飞轮"),
                Part(name="脚踏", category="传动系统", sku="P-DRIVE-003", stock_quantity=60, unit="对", description="防滑脚踏"),
                Part(name="车座", category="配件", sku="P-SEAT-001", stock_quantity=35, unit="个", description="舒适型车座"),
                Part(name="车铃", category="配件", sku="P-BELL-001", stock_quantity=100, unit="个", description="铝合金车铃"),
                Part(name="反光板", category="配件", sku="P-REFLECT-001", stock_quantity=120, unit="套", description="前后反光板套装"),
                Part(name="车把套", category="配件", sku="P-GRIP-001", stock_quantity=80, unit="对", description="橡胶防滑把套"),
                Part(name="润滑油", category="养护", sku="P-LUBE-001", stock_quantity=50, unit="瓶", description="自行车专用润滑油"),
                Part(name="除锈剂", category="养护", sku="P-RUST-001", stock_quantity=40, unit="瓶", description="金属除锈剂"),
                Part(name="螺丝套装", category="配件", sku="P-SCREW-001", stock_quantity=200, unit="套", description="标准螺丝套装"),
            ]
            for part in parts:
                db.add(part)
            db.commit()
            print(f"Created {len(parts)} parts.")

        if not db.query(Bike).filter(Bike.bike_code == "BK202401120001").first():
            print("Creating sample business data (complete flow)...")

            donor1 = db.query(User).filter(User.username == "donor1").first()
            donor2 = db.query(User).filter(User.username == "donor2").first()
            donor3 = db.query(User).filter(User.username == "donor3").first()
            volunteer1 = db.query(User).filter(User.username == "volunteer1").first()
            volunteer2 = db.query(User).filter(User.username == "volunteer2").first()
            recipient_user1 = db.query(User).filter(User.username == "donor1").first()
            recipient_user2 = db.query(User).filter(User.username == "donor2").first()
            recipient_user3 = db.query(User).filter(User.username == "donor3").first()
            admin = db.query(User).filter(User.username == "admin").first()

            base_date = datetime.now() - timedelta(days=30)

            bike1 = Bike(
                bike_code="BK202401120001",
                brand="凤凰", model="经典28大杠", color="黑色",
                bike_type="城市车", frame_size="28寸",
                condition_on_receipt="车架完好，轮胎老化，刹车不灵，链条生锈",
                status="donated_completed",
                received_at=base_date + timedelta(days=2)
            )
            db.add(bike1)
            db.flush()

            donation1 = Donation(
                donor_id=donor1.id, bike_id=bike1.id,
                description="家里闲置的老凤凰自行车，还能骑，就是有些地方生锈了",
                status="completed"
            )
            db.add(donation1)
            db.flush()

            history1 = [
                DonationHistory(donation_id=donation1.id, status="pending", description="捐赠登记成功，等待预约回收"),
                DonationHistory(donation_id=donation1.id, status="scheduled", description="已预约回收，时间：上午"),
                DonationHistory(donation_id=donation1.id, status="assigned", description=f"志愿者 {volunteer1.full_name} 已接单"),
                DonationHistory(donation_id=donation1.id, status="received", description=f"已回收成功，车辆编号：{bike1.bike_code}，进入翻新流程"),
                DonationHistory(donation_id=donation1.id, status="refurbishing", description="开始翻新 - 清洁除锈"),
                DonationHistory(donation_id=donation1.id, status="refurbishing", description="开始翻新 - 轮胎更换"),
                DonationHistory(donation_id=donation1.id, status="refurbishing", description="开始翻新 - 刹车系统检修"),
                DonationHistory(donation_id=donation1.id, status="refurbished", description=f"翻新完成，车辆编号：{bike1.bike_code}，等待匹配受赠人"),
                DonationHistory(donation_id=donation1.id, status="matched", description="已匹配给受赠人：赵小明"),
                DonationHistory(donation_id=donation1.id, status="completed", description="车辆已交付给受赠人，捐赠完成！"),
            ]
            for h in history1:
                db.add(h)

            pickup1 = Pickup(
                donation_id=donation1.id, volunteer_id=volunteer1.id,
                address="北京市朝阳区幸福小区3号楼2单元501",
                contact_name="王先生", contact_phone="13900000001",
                scheduled_date=(base_date + timedelta(days=2)).date(),
                scheduled_time="上午 9:00-11:00",
                status="completed", notes="捐赠人很热情，车放在楼下",
                completed_at=base_date + timedelta(days=2, hours=10)
            )
            db.add(pickup1)

            refurb1 = Refurbishment(
                bike_id=bike1.id, volunteer_id=volunteer1.id,
                stage="清洁除锈", description="全车清洁，车架除锈打磨",
                status="completed", labor_hours=3.0,
                started_at=base_date + timedelta(days=3, hours=9),
                completed_at=base_date + timedelta(days=3, hours=12),
                notes="锈迹比较严重，花了不少时间"
            )
            refurb2 = Refurbishment(
                bike_id=bike1.id, volunteer_id=volunteer2.id,
                stage="轮胎更换", description="更换前后内外胎",
                status="completed", labor_hours=2.5,
                started_at=base_date + timedelta(days=5, hours=14),
                completed_at=base_date + timedelta(days=5, hours=16, minutes=30),
                notes="原车胎已经开裂老化"
            )
            refurb3 = Refurbishment(
                bike_id=bike1.id, volunteer_id=volunteer1.id,
                stage="刹车系统检修", description="更换刹车线和刹车皮，调整刹车",
                status="completed", labor_hours=2.5,
                started_at=base_date + timedelta(days=8, hours=10),
                completed_at=base_date + timedelta(days=8, hours=12, minutes=30),
                notes="刹车系统全部换新"
            )
            db.add_all([refurb1, refurb2, refurb3])
            db.flush()

            part_inner = db.query(Part).filter(Part.sku == "P-TYRE-001").first()
            part_outer = db.query(Part).filter(Part.sku == "P-TYRE-002").first()
            part_brake_pad = db.query(Part).filter(Part.sku == "P-BRAKE-001").first()
            part_brake_cable = db.query(Part).filter(Part.sku == "P-BRAKE-002").first()
            part_lube = db.query(Part).filter(Part.sku == "P-LUBE-001").first()
            part_rust = db.query(Part).filter(Part.sku == "P-RUST-001").first()

            part_usages = [
                PartUsage(part_id=part_inner.id, bike_id=bike1.id, refurbishment_id=refurb2.id, quantity=2, notes="前后内胎各一条"),
                PartUsage(part_id=part_outer.id, bike_id=bike1.id, refurbishment_id=refurb2.id, quantity=2, notes="前后外胎各一条"),
                PartUsage(part_id=part_brake_pad.id, bike_id=bike1.id, refurbishment_id=refurb3.id, quantity=2, notes="前后刹车皮各一对"),
                PartUsage(part_id=part_brake_cable.id, bike_id=bike1.id, refurbishment_id=refurb3.id, quantity=2, notes="前后刹车线各一根"),
                PartUsage(part_id=part_lube.id, bike_id=bike1.id, refurbishment_id=refurb1.id, quantity=1, notes="全车链条润滑"),
                PartUsage(part_id=part_rust.id, bike_id=bike1.id, refurbishment_id=refurb1.id, quantity=1, notes="车架除锈"),
            ]
            for pu in part_usages:
                db.add(pu)

            recipient1 = Recipient(
                applicant_id=recipient_user1.id,
                full_name="赵小明", phone="13700000001",
                id_card="110101199001011234",
                address="北京市海淀区希望小学宿舍",
                applicant_type="学生", organization="希望小学",
                reason="家离学校远，每天走路要1小时，需要一辆自行车上下学",
                bike_type_preference="城市车", frame_size_preference="26寸",
                status="received", review_notes="情况属实，批准申请"
            )
            db.add(recipient1)
            db.flush()

            match1 = Match(
                bike_id=bike1.id, recipient_id=recipient1.id,
                matched_by=admin.id, status="delivered",
                notes="送到学校传达室",
                delivery_date=(base_date + timedelta(days=15)).date(),
                delivered_at=base_date + timedelta(days=15, hours=14)
            )
            db.add(match1)

            bike2 = Bike(
                bike_code="BK202401170002",
                brand="美利达", model="勇士500", color="红色",
                bike_type="山地车", frame_size="26寸",
                condition_on_receipt="车况良好，需要清洁保养，链条有些拉长",
                status="refurbishing",
                received_at=base_date + timedelta(days=7)
            )
            db.add(bike2)
            db.flush()

            donation2 = Donation(
                donor_id=donor2.id, bike_id=bike2.id,
                description="孩子长大了，骑不了了，美利达山地车，车况还不错",
                status="refurbishing"
            )
            db.add(donation2)
            db.flush()

            history2 = [
                DonationHistory(donation_id=donation2.id, status="pending", description="捐赠登记成功，等待预约回收"),
                DonationHistory(donation_id=donation2.id, status="scheduled", description="已预约回收，时间：下午"),
                DonationHistory(donation_id=donation2.id, status="assigned", description=f"志愿者 {volunteer2.full_name} 已接单"),
                DonationHistory(donation_id=donation2.id, status="received", description=f"已回收成功，车辆编号：{bike2.bike_code}，进入翻新流程"),
                DonationHistory(donation_id=donation2.id, status="refurbishing", description="开始翻新 - 清洁保养"),
            ]
            for h in history2:
                db.add(h)

            pickup2 = Pickup(
                donation_id=donation2.id, volunteer_id=volunteer2.id,
                address="北京市海淀区中关村小区8号楼1单元302",
                contact_name="刘女士", contact_phone="13900000002",
                scheduled_date=(base_date + timedelta(days=7)).date(),
                scheduled_time="下午 14:00-16:00",
                status="completed", notes="车很新，保养得不错",
                completed_at=base_date + timedelta(days=7, hours=15, minutes=30)
            )
            db.add(pickup2)

            refurb4 = Refurbishment(
                bike_id=bike2.id, volunteer_id=volunteer2.id,
                stage="清洁保养", description="全车清洁，上油保养",
                status="completed", labor_hours=2.5,
                started_at=base_date + timedelta(days=10, hours=9),
                completed_at=base_date + timedelta(days=10, hours=11, minutes=30),
                notes="车况不错，主要是清洁"
            )
            refurb5 = Refurbishment(
                bike_id=bike2.id, volunteer_id=volunteer1.id,
                stage="传动系统检修", description="检查链条、飞轮，调整变速",
                status="in_progress", labor_hours=1.0,
                started_at=base_date + timedelta(days=15, hours=14)
            )
            db.add_all([refurb4, refurb5])

            bike3 = Bike(
                bike_code="BK202401300003",
                brand="大行", model="BYA412", color="白色",
                bike_type="折叠车", frame_size="14寸",
                condition_on_receipt="折叠车，车况一般，需要全面检查",
                status="donated",
                received_at=base_date + timedelta(days=10)
            )
            db.add(bike3)
            db.flush()

            donation3 = Donation(
                donor_id=donor3.id, bike_id=bike3.id,
                description="旧的折叠自行车，放着落灰，希望能帮助到有需要的人",
                status="received"
            )
            db.add(donation3)
            db.flush()

            history3 = [
                DonationHistory(donation_id=donation3.id, status="pending", description="捐赠登记成功，等待预约回收"),
                DonationHistory(donation_id=donation3.id, status="scheduled", description="已预约回收，时间：上午"),
                DonationHistory(donation_id=donation3.id, status="received", description=f"已回收成功，车辆编号：{bike3.bike_code}，进入翻新流程"),
            ]
            for h in history3:
                db.add(h)

            pickup3 = Pickup(
                donation_id=donation3.id, volunteer_id=volunteer1.id,
                address="北京市西城区金融街小区5号楼",
                contact_name="陈先生", contact_phone="13900000003",
                scheduled_date=(base_date + timedelta(days=10)).date(),
                scheduled_time="上午 10:00-12:00",
                status="completed", notes="折叠车，体积小，方便运输",
                completed_at=base_date + timedelta(days=10, hours=11)
            )
            db.add(pickup3)

            donation4 = Donation(
                donor_id=donor1.id,
                description="两辆旧自行车，都是好的，搬家带不走了",
                status="scheduled"
            )
            db.add(donation4)
            db.flush()

            history4 = [
                DonationHistory(donation_id=donation4.id, status="pending", description="捐赠登记成功，等待预约回收"),
                DonationHistory(donation_id=donation4.id, status="scheduled", description="已预约回收，时间：下午"),
            ]
            for h in history4:
                db.add(h)

            pickup4 = Pickup(
                donation_id=donation4.id,
                address="北京市朝阳区幸福小区3号楼2单元501",
                contact_name="王先生", contact_phone="13900000001",
                scheduled_date=(base_date + timedelta(days=25)).date(),
                scheduled_time="下午 14:00-17:00",
                status="scheduled", notes="两辆车，需要带个大袋子装配件"
            )
            db.add(pickup4)

            recipient2 = Recipient(
                applicant_id=recipient_user2.id,
                full_name="孙华", phone="13700000002",
                id_card="110102198505055678",
                address="北京市朝阳区外来务工公寓",
                applicant_type="外来务工人员", organization="朝阳建筑公司",
                reason="上班地方离宿舍远，公交不方便，需要自行车通勤",
                bike_type_preference="城市车", frame_size_preference="26寸",
                status="approved", review_notes="批准，等待匹配"
            )
            recipient3 = Recipient(
                applicant_id=recipient_user3.id,
                full_name="周外来", phone="13700000003",
                id_card="340102199003032345",
                address="北京市海淀区打工子弟学校",
                applicant_type="外来务工人员", organization="海淀区清洁队",
                reason="环卫工人，每天片区巡逻需要代步工具",
                bike_type_preference="城市车", frame_size_preference="28寸",
                status="approved", review_notes="情况属实，优先匹配大尺寸"
            )
            recipient4 = Recipient(
                applicant_id=donor1.id,
                full_name="吴同学", phone="13700000004",
                id_card="110108200506067890",
                address="北京市门头沟山区中学",
                applicant_type="学生", organization="山区中学",
                reason="家住山区，学校远，需要自行车上下学",
                bike_type_preference="山地车", frame_size_preference="26寸",
                status="pending"
            )
            db.add_all([recipient2, recipient3, recipient4])

            db.commit()
            print("Sample business data created successfully.")

        print("\n" + "="*50)
        print("Database initialization complete!")
        print("="*50)
        print("\nDemo accounts (password: 123456):")
        print("  - admin      (管理员)")
        print("  - volunteer1 (志愿者 - 张志愿)")
        print("  - volunteer2 (志愿者 - 李爱心)")
        print("  - donor1     (捐赠人 - 王先生)")
        print("  - donor2     (捐赠人 - 刘女士)")
        print("  - donor3     (捐赠人 - 陈先生)")
        print("\nSample data includes:")
        print("  - 1 completed donation with full trace flow")
        print("  - 1 donation under refurbishment")
        print("  - 1 donation waiting for refurbishment")
        print("  - 1 donation waiting for pickup")
        print("  - 3 recipient applications (approved/pending)")
        print("  - 14 parts in stock")
        print("")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
