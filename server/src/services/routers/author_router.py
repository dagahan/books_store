from .base_router import *


def get_author_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/authors", tags=["authors"])
    base_router = BaseRouter(db)


    @router.get("/", status_code=status.HTTP_200_OK)
    async def get_all_authors(
        session = Depends(db.get_session)
    ) -> Union[List[AuthorDTO] | AuthorDTO]:
        
        result = await session.execute(
            select(Author)
        )
        row_items = result.scalars().all()

        if not row_items:
            raise HTTPException(status_code=404, detail="There are no authors")

        return base_router.validate_models_by_schema(row_items, AuthorDTO)


    @router.get("/{author_id}", status_code=status.HTTP_200_OK)
    async def get_author_by_id(
        author_id: PythonUUID,
        session = Depends(db.get_session)
    ) -> AuthorDTO:
        
        result = await session.execute(
            select(Author)
            .where(Author.id == author_id)
        )
        author = result.scalars().first()

        if not author:
            logger.warning(f"Author with ID {author_id} not found.")
            raise HTTPException(status_code=404, detail="Author not found")
        
        return base_router.validate_models_by_schema(author, AuthorDTO)


    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create_author(
        author_data: AuthorCreateDTO,
        session = Depends(db.get_session)
    ):
        new_author = Author(name=author_data.name)

        session.add(new_author)
        await session.commit()
        
        logger.info(f"Created new author with ID: {new_author.id}")
        return {"message": {"UUID": f"{new_author.id}"}}


    @router.patch("/{author_id}", status_code=status.HTTP_200_OK)
    async def update_author(
        author_id: PythonUUID,
        update_data: AuthorUpdateDTO,
        session = Depends(db.get_session)
    ):
        result = await session.execute(
            select(Author)
            .where(Author.id == author_id)
            .options(noload("*"))
        )
        author = result.scalar_one_or_none()

        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for key, value in update_dict.items():
            setattr(author, key, value)

        await session.commit()
        logger.info(f"Updated author with ID: {author_id}")
        return Response(status_code=status.HTTP_200_OK)


    @router.delete("/{author_id}", status_code=status.HTTP_200_OK)
    async def delete_author(
        author_id: PythonUUID,
        session = Depends(db.get_session)
    ):
        result = await session.execute(
            select(Author)
            .where(Author.id == author_id)
        )
        author = result.scalar_one_or_none()

        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        
        await session.delete(author)
        await session.commit()

        logger.info(f"Deleted author with ID: {author_id}")
        return Response(status_code=status.HTTP_200_OK)

    
    return router