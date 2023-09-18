from flask_smorest import Blueprint,abort
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from db import db
from flask.views import MethodView
from models import TagModel,StoreModel,ItemModel
from schemas import TagSchema,TagAndItemSchema

blp=Blueprint("Tags","tags",description="Operation on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsinStore(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self,store_id):
        store=StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201,TagSchema)
    def post(self,tag_data,store_id):
        tag=TagModel(**tag_data,store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500,message=str(e))
        return tag

@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkandUnlinkTags(MethodView):
    @blp.arguments(TagAndItemSchema)
    @blp.response(201,TagSchema)
    def post(self,item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)
        if item.store.id != tag.store.id:
            abort(400, message="Make sure item and tag belong to the same store before linking.")
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An error occured while linking the tag")
        return tag

    @blp.response(201,TagAndItemSchema)
    def delete(self,item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)
        if item.store.id != tag.store.id:
            abort(400, message="Make sure item and tag belong to the same store before linking.")

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An error occured while deleting the tag")
        return {"messsage":"Item removed from tag","item":item,"tag":tag}



@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200,TagSchema)
    def get(self,tag_id):
        return TagModel.query.get_or_404(tag_id)

    @blp.response(202,TagSchema,description="Deleting a tag independent of any item",example={"message":"Tag Deleted"})
    @blp.alt_response(404,description="Tag Not Found")
    @blp.alt_response(400,description="Items are associated with tag")
    def delete(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit
            return {"message":"Tag deleted successfully"}

        abort(400,message="Could not delete tag,Make sure it is not linked to any item")
        




    
